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
        SELECT flight_number, status, source, destination
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
            "source": row[2],
            "destination": row[3]
        })
    
    return flights