# helper_cron_jobs.py
# Background cron jobs for automatic notifications

import logging
from datetime import datetime, timedelta
import pymysql
import os
from dotenv import load_dotenv
from pathlib import Path

from flask_app.constants import (
    REMINDER_INTERVAL_EARLY,
    REMINDER_INTERVAL_MIDDLE,
    REMINDER_INTERVAL_FINAL,
    REMINDER_WINDOW_EARLY_MIN,
    REMINDER_WINDOW_EARLY_MAX,
    REMINDER_WINDOW_MIDDLE_MIN,
    REMINDER_WINDOW_MIDDLE_MAX,
    REMINDER_WINDOW_FINAL_MIN,
    REMINDER_WINDOW_FINAL_MAX,
    FLIGHT_CLEANUP_MINUTES,
    SCHED_CHECK_INTERVAL,
    DB_CONNECT_TIMEOUT_SECONDS
)

logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# In-memory cache to track which reminders have been sent
# Format: {flight_id: {30: True, 15: True, 5: True}}
# This resets when Flask restarts (which is acceptable for development)
reminder_cache = {}

# Singleton scheduler instance to prevent duplicates
_scheduler_instance = None


def get_db_connection():
    """Get database connection"""
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "hfxair"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", "3306")),
        connect_timeout=DB_CONNECT_TIMEOUT_SECONDS
    )


def check_departure_reminders():
    """
    Cron job: Every minute, check for flights departing within next 30 minutes
    and send reminders ONLY at 30, 15, and 5 minute intervals before departure
    Tracking is done in-memory to avoid adding extra database tables
    """
    global reminder_cache
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get current time
        now = datetime.utcnow()
        reminder_window_start = now
        reminder_window_end = now + timedelta(minutes=REMINDER_INTERVAL_EARLY)

        # Query flights departing soon (within 30 minutes)
        # Status should be 'Boarding' or earlier (not yet departed)
        cur.execute("""
            SELECT f.flight_id, f.flight_number, f.departure_time, f.status, f.gate, f.terminal
            FROM flights f
            WHERE f.status NOT IN ('Departed', 'Cancelled', 'Arrived')
            AND f.departure_time BETWEEN %s AND %s
            AND f.departure_time IS NOT NULL
            ORDER BY f.departure_time ASC
        """, (reminder_window_start, reminder_window_end))

        flights = cur.fetchall()
        logger.info(f"Found {len(flights)} flights departing within {REMINDER_INTERVAL_EARLY} minutes")

        # Send reminders for each flight
        for flight in flights:
            flight_id, flight_number, departure_time, status, gate, terminal = flight
            
            # Calculate minutes until departure
            minutes_until = int((departure_time - now).total_seconds() / 60)
            
            # Determine which reminder interval this falls into (30, 15, or 5 minutes)
            reminder_interval = None
            if REMINDER_WINDOW_EARLY_MIN <= minutes_until <= REMINDER_WINDOW_EARLY_MAX:
                reminder_interval = REMINDER_INTERVAL_EARLY
            elif REMINDER_WINDOW_MIDDLE_MIN <= minutes_until <= REMINDER_WINDOW_MIDDLE_MAX:
                reminder_interval = REMINDER_INTERVAL_MIDDLE
            elif REMINDER_WINDOW_FINAL_MIN <= minutes_until <= REMINDER_WINDOW_FINAL_MAX:
                reminder_interval = REMINDER_INTERVAL_FINAL
            
            # Only send if we're in one of the reminder windows
            if reminder_interval:
                # Initialize cache entry for this flight if not exists
                if flight_id not in reminder_cache:
                    reminder_cache[flight_id] = {}
                
                # Check if reminder has already been sent for this interval
                if reminder_interval not in reminder_cache[flight_id] or not reminder_cache[flight_id][reminder_interval]:
                    # Query subscribers for this flight
                    cur.execute("""
                        SELECT DISTINCT expo_token FROM user_subscriptions 
                        WHERE flight_id = %s AND expo_token IS NOT NULL
                    """, (flight_id,))
                    
                    tokens = [row[0] for row in cur.fetchall() if row[0]]
                    
                    if tokens:
                        # Build notification message based on interval
                        title = f"Flight {flight_number} Reminder"
                        if reminder_interval == REMINDER_INTERVAL_EARLY:
                            body = f"Your flight {flight_number} departs in {REMINDER_INTERVAL_EARLY} minutes. Gate: {gate or 'TBA'}"
                        elif reminder_interval == REMINDER_INTERVAL_MIDDLE:
                            body = f"Your flight {flight_number} departs in {REMINDER_INTERVAL_MIDDLE} minutes. Please head to gate {gate or 'TBA'}"
                        else:  # Final reminder
                            body = f"Your flight {flight_number} departs in {REMINDER_INTERVAL_FINAL} minutes! Get to gate {gate or 'TBA'} NOW!"
                        
                        # Send notifications
                        from flask_app.helper.helper_firebase_notification import notify_subscribers
                        result = notify_subscribers(flight_id=flight_id, title=title, body=body)
                        
                        logger.info(f"Sent {reminder_interval}-min reminder for {flight_number}: {result}")
                        
                        # Mark reminder as sent in cache
                        reminder_cache[flight_id][reminder_interval] = True
            else:
                # If flight is beyond 30 min window, reset cache so reminders can be sent again if departure is delayed
                if flight_id in reminder_cache and minutes_until < FLIGHT_CLEANUP_MINUTES:
                    # Flight has departed or passed all reminder windows
                    del reminder_cache[flight_id]

        cur.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error in check_departure_reminders: {e}")


def check_flight_updates():
    """
    Cron job: Every minute, check for flight data changes and send notifications
    Changes are detected by comparing with in-memory cache
    """
    global reminder_cache
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get all flights
        cur.execute("""
            SELECT f.flight_id, f.flight_number, f.status, f.gate, f.terminal,
                   f.departure_time, f.arrival_time, f.boarding_time
            FROM flights f
            WHERE f.departure_time IS NOT NULL
            ORDER BY f.flight_id
        """)

        flights = cur.fetchall()
        
        for flight in flights:
            flight_id, flight_number, status, gate, terminal, departure_time, arrival_time, boarding_time = flight
            
            # Build current flight state
            current_state = {
                "status": status,
                "gate": gate,
                "departure_time": departure_time,
                "arrival_time": arrival_time
            }
            
            # Check if this flight was previously cached
            if flight_id not in reminder_cache:
                reminder_cache[flight_id] = {"state": current_state}
                continue
            
            # Get previous state
            previous_state = reminder_cache[flight_id].get("state", {})
            
            # Detect changes
            changes = {}
            if previous_state.get("status") != current_state["status"]:
                changes["status"] = (previous_state.get("status"), current_state["status"])
            if previous_state.get("gate") != current_state["gate"]:
                changes["gate"] = (previous_state.get("gate"), current_state["gate"])
            if previous_state.get("departure_time") != current_state["departure_time"]:
                changes["departure_time"] = (previous_state.get("departure_time"), current_state["departure_time"])
            if previous_state.get("arrival_time") != current_state["arrival_time"]:
                changes["arrival_time"] = (previous_state.get("arrival_time"), current_state["arrival_time"])
            
            # If changes detected, send notification
            if changes:
                # Build smart notification based on what changed
                title = f"Update: {flight_number}"
                body = ""
                
                if "status" in changes:
                    old_status, new_status = changes["status"]
                    if new_status == "Departed":
                        body = f"Flight {flight_number} has departed!"
                    elif new_status == "Arrived":
                        body = f"Flight {flight_number} has arrived!"
                    elif new_status == "Cancelled":
                        body = f"Flight {flight_number} has been cancelled."
                    elif new_status == "Delayed":
                        body = f"Flight {flight_number} is now delayed."
                    else:
                        body = f"Flight {flight_number} status: {new_status}"
                
                if "gate" in changes:
                    old_gate, new_gate = changes["gate"]
                    body = f"Flight {flight_number} gate changed from {old_gate or 'TBA'} to {new_gate or 'TBA'}"
                
                if "departure_time" in changes and "status" not in changes:
                    old_time, new_time = changes["departure_time"]
                    if old_time and new_time:
                        old_hour = old_time.strftime("%H:%M")
                        new_hour = new_time.strftime("%H:%M")
                        body = f"Flight {flight_number} departure time changed from {old_hour} to {new_hour}"
                
                if "arrival_time" in changes and "status" not in changes:
                    old_time, new_time = changes["arrival_time"]
                    if old_time and new_time:
                        old_hour = old_time.strftime("%H:%M")
                        new_hour = new_time.strftime("%H:%M")
                        body = f"Flight {flight_number} arrival time changed from {old_hour} to {new_hour}"
                
                if body:
                    # Send notifications
                    from flask_app.helper.helper_firebase_notification import notify_subscribers
                    result = notify_subscribers(flight_id=flight_id, title=title, body=body)
                    logger.info(f"Sent flight update notification for {flight_number}: {result}")
            
            # Update cache with current state
            reminder_cache[flight_id]["state"] = current_state

        cur.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error in check_flight_updates: {e}")


def start_background_jobs(app):
    """
    Initialize and start all background cron jobs
    Should be called from Flask app
    """
    global _scheduler_instance
    
    # Prevent multiple scheduler instances
    if _scheduler_instance is not None and _scheduler_instance.running:
        logger.info("Scheduler already running, skipping initialization")
        return _scheduler_instance
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        
        _scheduler_instance = BackgroundScheduler()
        
        # DISABLED: Departure reminders (30/15/5 min)
        # Uncomment below to re-enable
        # _scheduler_instance.add_job(
        #     func=check_departure_reminders,
        #     trigger="interval",
        #     minutes=SCHED_CHECK_INTERVAL,
        #     id="departure_reminders",
        #     name="Check departure reminders",
        #     replace_existing=True
        # )
        
        # Check flight updates every minute
        _scheduler_instance.add_job(
            func=check_flight_updates,
            trigger="interval",
            minutes=SCHED_CHECK_INTERVAL,
            id="flight_updates",
            name="Check flight updates",
            replace_existing=True
        )
        
        # Start the scheduler
        if not _scheduler_instance.running:
            _scheduler_instance.start()
            logger.info("Background scheduler started successfully")
            logger.info(f"Jobs: flight_updates (every {SCHED_CHECK_INTERVAL} min)")
        
        return _scheduler_instance
        
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {e}")
        return None