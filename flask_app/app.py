# app.py
from flask import Flask, request, jsonify
import jwt
import pymysql
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

from .auth import require_auth
from .helper.helper_firebase_notification import send_push


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
TOKEN_EXPIRY_HOURS = 24
SECRET = "hfxair-app-secret"


def get_db_connection():

    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "hfxair"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", "3306")),
        connect_timeout=5
    )


@app.post("/send-notification")
def send_notification():
    data = request.json
    token = data.get("token")
    title = data.get("title", "Default title")
    body = data.get("body", "Default body")
    success = send_push(token, title, body)
    return jsonify({"success": success})


@app.route('/')
def home():
    return jsonify({"message": "Welcome to HFX AIR, your local airport app!"})


def check_empty(data):
    """Validate that required fields are present and not empty/None"""
    if not data:
        return jsonify({"error": "Missing required fields"}), 400
    
    flight_number = data.get("flight_number")
    ticket_number = data.get("ticket_number")
    
    if not flight_number or not ticket_number:
        return jsonify({"error": "Missing required fields"}), 400
    
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
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid flight or ticket"}), 401


@app.get("/protected-test")
@require_auth(SECRET)
def protected_test():
    return jsonify({"message": "Access granted"}), 200


@app.get("/flights")
def get_flights():
    flights = get_all_flights()
    return jsonify(flights), 200

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
        if row[5]:  # departure_time
            scheduled_time = row[5].strftime("%H:%M") if isinstance(row[5], datetime) else str(row[5])[:5]
        
        # Format actual time as HH:MM
        actual_time = None
        if row[6]:  # actual_departure_time
            actual_time = row[6].strftime("%H:%M") if isinstance(row[6], datetime) else str(row[6])[:5]
        
        flights.append({
            "id": str(row[0]),  # flight_id
            "flightNumber": row[1],  # flight_number
            "airline": row[2],  # airline_name
            "from": row[3],  # origin
            "to": row[4],  # destination
            "scheduledTime": scheduled_time,
            "actualTime": actual_time,
            "status": row[7] if row[7] else "Scheduled",  # status
            "gate": row[8] if row[8] else None,  # gate
            "terminal": row[9] if row[9] else None,  # terminal
            "baggage": None,  # Not in schema
            "notificationsEnabled": False  # Default to false
        })
    
    return flights


@app.get("/flights/<int:flight_id>")
def get_flight_details(flight_id):
    flight = get_flight_by_id(flight_id)
    if flight:
        return jsonify(flight), 200
    return jsonify({"error": "Flight not found"}), 404


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
            "flight_number": row[0],
            "status": row[1],
            "origin": row[2],
            "destination": row[3]
        }
    return None

@app.get("/flights/arrivals")
def arrivals():
    flights = get_arrivals()
    return jsonify(flights), 200

@app.get("/flights/departures")
def departures():
    flights = get_departures()
    return jsonify(flights), 200


def get_arrivals():
    conn = get_db_connection()
    cur = conn.cursor()
    # Query flights where destination matches the airport (e.g., Halifax)
    airport = os.getenv("AIRPORT_NAME", "Halifax")
    query = """
        SELECT flight_number, status, origin, destination, arrival_time
        FROM flights
        WHERE destination = %s
        ORDER BY flight_number
    """
    cur.execute(query, (airport,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert rows to list of dictionaries
    arrivals = []
    for row in rows:
        arrivals.append({
            "flight_number": row[0],
            "origin": row[2],
            "destination": row[3],
            "status": row[1],
            "arrival_time": row[4].isoformat() if row[4] else None
        })
    
    return arrivals

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
    departures = []
    for row in rows:
        # Format scheduled time as HH:MM
        scheduled_time = None
        if row[4]:  # departure_time
            scheduled_time = row[4].strftime("%H:%M") if isinstance(row[4], datetime) else str(row[4])[:5]
        
        # Format actual time as HH:MM
        actual_time = None
        if row[5]:  # actual_departure_time
            actual_time = row[5].strftime("%H:%M") if isinstance(row[5], datetime) else str(row[5])[:5]
        
        # Format boarding time as HH:MM
        boarding_time = None
        if row[9]:  # boarding_time
            boarding_time = row[9].strftime("%H:%M") if isinstance(row[9], datetime) else str(row[9])[:5]
        
        departures.append({
            "id": str(row[0]),  # flight_id
            "flightNumber": row[1],  # flight_number
            "airline": row[2],  # airline_name
            "to": row[3],  # destination
            "scheduledTime": scheduled_time,
            "actualTime": actual_time,
            "status": row[6] if row[6] else "Scheduled",  # status
            "gate": row[7] if row[7] else None,  # gate
            "terminal": row[8] if row[8] else None,  # terminal
            "boardingTime": boarding_time,
            "notificationsEnabled": False  # Default to false
        })
    
    return departures



@app.post("/subscribe")
@require_auth(SECRET)
def subscribe():
    data = request.json or {}
    flight_id = data.get("flight_id")
    expo_token = data.get("expo_token")

    if not flight_id or not expo_token:
        return jsonify({"error": "Missing fields"}), 400

    ticket_no = request.user["ticket_no"]
    save_subscription(ticket_no, flight_id, expo_token)
    return jsonify({"message": "Subscribed"}), 200


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