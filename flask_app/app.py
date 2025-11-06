# app.py
from flask import Flask, request, jsonify
import jwt
import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path



# Load environment variables from .env file
# Get the directory where this file is located
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
TOKEN_EXPIRY_HOURS = 24
SECRET = "hfxair-app-secret"


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
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "airportdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "yourpassword")
    )
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


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return wrapper

@app.get("/flights")
def get_flights():
    flights = get_all_flights()
    return jsonify(flights), 200

def get_all_flights():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "airportdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "yourpassword")
    )
    cur = conn.cursor()
    query = """
        SELECT flight_number, status, origin, destination
        FROM flights
        ORDER BY flight_number
    """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert rows to list of dictionaries
    flights = []
    for row in rows:
        flights.append({
            "flight_number": row[0],
            "status": row[1],
            "origin": row[2],
            "destination": row[3]
        })
    
    return flights


@app.get("/flights/<int:flight_id>")
def get_flight_details(flight_id):
    flight = get_flight_by_id(flight_id)
    if flight:
        return jsonify(flight), 200
    return jsonify({"error": "Flight not found"}), 404


def get_flight_by_id(flight_id):    
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "airportdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "yourpassword")
    )
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
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "airportdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "yourpassword")
    )
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
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "airportdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "yourpassword")
    )
    cur = conn.cursor()
    # Query flights where origin matches the airport
    airport = os.getenv("AIRPORT_NAME", "Halifax")
    query = """
        SELECT flight_number, status, origin, destination, departure_time
        FROM flights
        WHERE origin = %s
        ORDER BY flight_number
    """
    cur.execute(query, (airport,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert rows to list of dictionaries
    departures = []
    for row in rows:
        departures.append({
            "flight_number": row[0],
            "origin": row[2],
            "destination": row[3],
            "status": row[1],
            "departure_time": row[4].isoformat() if row[4] else None
        })
    
    return departures

