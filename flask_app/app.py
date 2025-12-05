# app.py
from flask import Flask, request, jsonify
import jwt
import pymysql
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

from flask_app.auth import require_auth
from flask_app.helper.helper_firebase_notification import send_push, notify_subscribers
from flask_app.helper.helper_cron_jobs import start_background_jobs
from flask_app.constants import (
    HTTP_OK,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_ERROR,
    TOKEN_EXPIRY_HOURS,
    DB_CONNECT_TIMEOUT_SECONDS,
    # Flight query column indices
    FLIGHT_COL_ID,
    FLIGHT_COL_NUMBER,
    FLIGHT_COL_AIRLINE,
    FLIGHT_COL_ORIGIN,
    FLIGHT_COL_DESTINATION,
    FLIGHT_COL_DEPARTURE,
    FLIGHT_COL_ACTUAL_DEPARTURE,
    FLIGHT_COL_STATUS,
    FLIGHT_COL_GATE,
    FLIGHT_COL_TERMINAL,
    FLIGHT_DETAIL_NUMBER,
    FLIGHT_DETAIL_STATUS,
    FLIGHT_DETAIL_ORIGIN,
    FLIGHT_DETAIL_DEST,
    ARRIVAL_COL_ID,
    ARRIVAL_COL_NUMBER,
    ARRIVAL_COL_AIRLINE,
    ARRIVAL_COL_ORIGIN,
    ARRIVAL_COL_DESTINATION,
    ARRIVAL_COL_SCHEDULED,
    ARRIVAL_COL_ACTUAL,
    ARRIVAL_COL_STATUS,
    ARRIVAL_COL_GATE,
    ARRIVAL_COL_TERMINAL,
    ARRIVAL_COL_BAGGAGE,
    DEPART_COL_ID,
    DEPART_COL_NUMBER,
    DEPART_COL_AIRLINE,
    DEPART_COL_DESTINATION,
    DEPART_COL_SCHEDULED,
    DEPART_COL_ACTUAL,
    DEPART_COL_STATUS,
    DEPART_COL_GATE,
    DEPART_COL_TERMINAL,
    DEPART_COL_BOARDING
)


# Load environment variables from .env file
# Get the directory where this file is located
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['DEBUG'] = True
SECRET = "hfxair-app-secret"

# Initialize background cron jobs
scheduler = start_background_jobs(app)


def get_db_connection():

    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "hfxair"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", "3306")),
        connect_timeout=DB_CONNECT_TIMEOUT_SECONDS
    )


@app.post("/send-notification")
def send_notification():
    data = request.json
    # Accept either a single token or a ticket_no/flight_id to notify subscribers
    token = data.get("token")
    ticket_no = data.get("ticket_no")
    flight_id = data.get("flight_id")
    title = data.get("title", "Default title")
    body = data.get("body", "Default body")

    if token:
        success = send_push(token, title, body)
        return jsonify({"success": success}), (HTTP_OK if success else HTTP_INTERNAL_ERROR)

    # If ticket_no or flight_id provided, send to all subscribers
    if ticket_no or flight_id:
        summary = notify_subscribers(
            ticket_no=ticket_no,
            flight_id=flight_id,
            title=title,
            body=body
        )
        return jsonify({"summary": summary}), HTTP_OK

    return jsonify({
        "error": "Provide 'token' or 'ticket_no'/'flight_id' in request body"
    }), HTTP_BAD_REQUEST


@app.route('/')
def home():
    return jsonify({"message": "Welcome to HFX AIR, your local airport app!"})


def check_empty(data):
    """Validate that required fields are present and not empty/None"""
    if not data:
        return jsonify({"error": "Missing required fields"}), HTTP_BAD_REQUEST
    
    flight_number = data.get("flight_number")
    ticket_number = data.get("ticket_number")
    
    if not flight_number or not ticket_number:
        return jsonify({"error": "Missing required fields"}), HTTP_BAD_REQUEST
    
    return None


def check_db_for_ticket(flight_no, ticket_no):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT 1 FROM tickets t
        JOIN flights f ON t.flight_id = f.flight_id
        WHERE f.flight_number = %s AND t.ticket_number = %s
        LIMIT 1
    """
    cur.execute(query, (flight_no, ticket_no))
    found = cur.fetchone()
    cur.close()
    conn.close()
    return bool(found)


def create_token(flight_no, ticket_no):
    payload = {
        "flight_no": flight_no,
        "ticket_no": ticket_no,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


# login route
@app.post("/login")
def login():
    data = request.json
    
    # Validate required fields are present and not empty/None
    error_response = check_empty(data)
    if error_response:
        return error_response
    
    flight_number = data.get("flight_number")
    ticket_number = data.get("ticket_number")
    
    if check_db_for_ticket(flight_number, ticket_number):
        token = create_token(flight_number, ticket_number)
        return jsonify({"token": token}), HTTP_OK
    return jsonify({"error": "Invalid flight or ticket"}), HTTP_UNAUTHORIZED


@app.get("/protected-test")
@require_auth(SECRET)
def protected_test():
    return jsonify({"message": "Access granted"}), HTTP_OK


@app.get("/flights")
def get_flights():
    flights = get_all_flights()
    return jsonify(flights), HTTP_OK


def get_all_flights():
    logging.info("connecting db")
    try:
        conn = get_db_connection()
    except Exception as e:
        logging.error(f"db connection failed: {e}")
        raise
    
    cur = conn.cursor()
    query = """
        SELECT 
            f.flight_id,
            f.flight_number,
            COALESCE(a.name, 'Unknown Airline') as airline_name,
            f.origin,
            f.destination,
            f.departure_time,
            fsu.actual_departure_time,
            COALESCE(fsu.current_status, f.status) as status,
            f.gate,
            f.terminal
        FROM flights f
        LEFT JOIN airlines a ON f.airline_id = a.airline_id
        LEFT JOIN flight_status_updates fsu ON f.flight_id = fsu.flight_id
            AND fsu.update_id = (
                SELECT MAX(update_id) 
                FROM flight_status_updates 
                WHERE flight_id = f.flight_id
            )
        ORDER BY f.flight_number
    """
    logging.info("fetching")
    cur.execute(query)
    rows = cur.fetchall()
    logging.info(f"fetched {len(rows)} rows")
    cur.close()
    conn.close()
    
    # Convert rows to list of dictionaries
    flights = []
    for row in rows:
        # Format scheduled time as HH:MM
        scheduled_time = None
        if row[FLIGHT_COL_DEPARTURE]:
            scheduled_time = (row[FLIGHT_COL_DEPARTURE].strftime("%H:%M")
                            if isinstance(row[FLIGHT_COL_DEPARTURE], datetime)
                            else str(row[FLIGHT_COL_DEPARTURE])[:5])
        
        # Format actual time as HH:MM
        actual_time = None
        if row[FLIGHT_COL_ACTUAL_DEPARTURE]:
            actual_time = (row[FLIGHT_COL_ACTUAL_DEPARTURE].strftime("%H:%M")
                          if isinstance(row[FLIGHT_COL_ACTUAL_DEPARTURE], datetime)
                          else str(row[FLIGHT_COL_ACTUAL_DEPARTURE])[:5])
        
        flights.append({
            "id": str(row[FLIGHT_COL_ID]),
            "flightNumber": row[FLIGHT_COL_NUMBER],
            "airline": row[FLIGHT_COL_AIRLINE],
            "from": row[FLIGHT_COL_ORIGIN],
            "to": row[FLIGHT_COL_DESTINATION],
            "scheduledTime": scheduled_time,
            "actualTime": actual_time,
            "status": row[FLIGHT_COL_STATUS] if row[FLIGHT_COL_STATUS] else "Scheduled",
            "gate": row[FLIGHT_COL_GATE] if row[FLIGHT_COL_GATE] else None,
            "terminal": row[FLIGHT_COL_TERMINAL] if row[FLIGHT_COL_TERMINAL] else None,
            "baggage": None,
            "notificationsEnabled": False
        })
    
    return flights


@app.get("/flights/<int:flight_id>")
def get_flight_details(flight_id):
    flight = get_flight_by_id(flight_id)
    if flight:
        return jsonify(flight), HTTP_OK
    return jsonify({"error": "Flight not found"}), HTTP_NOT_FOUND


def get_flight_by_id(flight_id):    
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT flight_number, status, origin, destination
        FROM flights
        WHERE flight_id = %s
    """
    cur.execute(query, (flight_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return {
            "flight_number": row[FLIGHT_DETAIL_NUMBER],
            "status": row[FLIGHT_DETAIL_STATUS],
            "origin": row[FLIGHT_DETAIL_ORIGIN],
            "destination": row[FLIGHT_DETAIL_DEST]
        }
    return None


@app.get("/flights/arrivals")
def arrivals():
    flights = get_arrivals()
    return jsonify(flights), HTTP_OK


@app.get("/flights/departures")
def departures():
    flights = get_departures()
    return jsonify(flights), HTTP_OK


def get_arrivals():
    conn = get_db_connection()
    cur = conn.cursor()
    # Query flights where destination matches the airport (e.g., Halifax)
    airport = os.getenv("AIRPORT_NAME", "Halifax")
    query = """
        SELECT 
            f.flight_id,
            f.flight_number,
            COALESCE(a.name, 'Unknown Airline') as airline_name,
            f.origin,
            f.destination,
            f.arrival_time,
            fsu.actual_arrival_time,
            COALESCE(fsu.current_status, f.status) as status,
            f.gate,
            f.terminal,
            f.baggage
        FROM flights f
        LEFT JOIN airlines a ON f.airline_id = a.airline_id
        LEFT JOIN flight_status_updates fsu ON f.flight_id = fsu.flight_id
            AND fsu.update_id = (
                SELECT MAX(update_id) 
                FROM flight_status_updates 
                WHERE flight_id = f.flight_id
            )
        WHERE f.destination = %s
        ORDER BY f.flight_number
    """
    cur.execute(query, (airport,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert rows to list of dictionaries
    arrivals_list = []
    for row in rows:
        
        # Format actual time as HH:MM
        actual_time = None
        if row[ARRIVAL_COL_ACTUAL]:
            actual_time = (row[ARRIVAL_COL_ACTUAL].strftime("%H:%M")
                          if isinstance(row[ARRIVAL_COL_ACTUAL], datetime)
                          else str(row[ARRIVAL_COL_ACTUAL])[:5])
        
        arrivals_list.append({
            "id": str(row[ARRIVAL_COL_ID]),
            "flightNumber": row[ARRIVAL_COL_NUMBER],
            "airline": row[ARRIVAL_COL_AIRLINE],
            "from": row[ARRIVAL_COL_ORIGIN],
            "to": row[ARRIVAL_COL_DESTINATION],
            "scheduledTime": row[ARRIVAL_COL_SCHEDULED],
            "actualTime": (row[ARRIVAL_COL_ACTUAL] if row[ARRIVAL_COL_ACTUAL]
                          else row[ARRIVAL_COL_SCHEDULED]),
            "status": (row[ARRIVAL_COL_STATUS] if row[ARRIVAL_COL_STATUS]
                      else "Scheduled"),
            "gate": row[ARRIVAL_COL_GATE] if row[ARRIVAL_COL_GATE] else None,
            "terminal": (row[ARRIVAL_COL_TERMINAL] if row[ARRIVAL_COL_TERMINAL]
                        else None),
            "baggage": (row[ARRIVAL_COL_BAGGAGE] if row[ARRIVAL_COL_BAGGAGE]
                       else None),
            "notificationsEnabled": False
        })
    
    return arrivals_list


def get_departures():
    conn = get_db_connection()
    cur = conn.cursor()
    # Query flights where origin matches the airport
    airport = os.getenv("AIRPORT_NAME", "Halifax")
    query = """
        SELECT 
            f.flight_id,
            f.flight_number,
            COALESCE(a.name, 'Unknown Airline') as airline_name,
            f.destination,
            f.departure_time,
            fsu.actual_departure_time,
            COALESCE(fsu.current_status, f.status) as status,
            f.gate,
            f.terminal,
            f.boarding_time
        FROM flights f
        LEFT JOIN airlines a ON f.airline_id = a.airline_id
        LEFT JOIN flight_status_updates fsu ON f.flight_id = fsu.flight_id
            AND fsu.update_id = (
                SELECT MAX(update_id) 
                FROM flight_status_updates 
                WHERE flight_id = f.flight_id
            )
        WHERE f.origin = %s
        ORDER BY f.flight_number
    """
    cur.execute(query, (airport,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert rows to list of dictionaries
    departures_list = []
    for row in rows:

        # Format boarding time as HH:MM
        boarding_time = None
        if row[DEPART_COL_BOARDING]:
            boarding_time = (row[DEPART_COL_BOARDING].strftime("%H:%M")
                            if isinstance(row[DEPART_COL_BOARDING], datetime)
                            else str(row[DEPART_COL_BOARDING])[:5])
        
        departures_list.append({
            "id": str(row[DEPART_COL_ID]),
            "flightNumber": row[DEPART_COL_NUMBER],
            "airline": row[DEPART_COL_AIRLINE],
            "to": row[DEPART_COL_DESTINATION],
            "scheduledTime": row[DEPART_COL_SCHEDULED],
            "actualTime": (row[DEPART_COL_ACTUAL] if row[DEPART_COL_ACTUAL]
                          else row[DEPART_COL_SCHEDULED]),
            "status": (row[DEPART_COL_STATUS] if row[DEPART_COL_STATUS]
                      else "Scheduled"),
            "gate": row[DEPART_COL_GATE] if row[DEPART_COL_GATE] else None,
            "terminal": row[DEPART_COL_TERMINAL] if row[DEPART_COL_TERMINAL] else None,
            "boardingTime": boarding_time,
            "notificationsEnabled": False
        })
    
    return departures_list


@app.post("/subscribe")
@require_auth(SECRET)
def subscribe():
    data = request.json or {}
    flight_id = data.get("flight_id")
    expo_token = data.get("expo_token")

    if not flight_id or not expo_token:
        return jsonify({"error": "Missing fields"}), HTTP_BAD_REQUEST

    ticket_no = request.user["ticket_no"]
    save_subscription(ticket_no, flight_id, expo_token)
    return jsonify({"message": "Subscribed"}), HTTP_OK


def save_subscription(ticket_no, flight_id, expo_token):
    """
    Save user subscription to database.
    Inserts subscription record, ignoring duplicates (INSERT IGNORE).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT IGNORE INTO user_subscriptions (ticket_no, flight_id, expo_token)
        VALUES (%s, %s, %s)
    """, (ticket_no, flight_id, expo_token))
    conn.commit()
    cur.close()
    conn.close()


# Import shop routes at the end to avoid circular import
# The app object must be created first before shop.py can import it
import flask_app.shop  # noqa: E402
import flask_app.booking  # noqa: E402