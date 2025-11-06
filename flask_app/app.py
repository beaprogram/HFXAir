# app.py
from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
app = Flask(__name__)
TOKEN_EXPIRY_HOURS = 24
SECRET = "hfxair-app-secret"


# login route
@app.post("/login")
def login():
    data = request.json
    
    # Validate required fields are present and not empty/None
    if not data:
        return jsonify({"error": "Missing required fields"}), 400
    
    flight_number = data.get("flight_number")
    ticket_number = data.get("ticket_number")
    
    if not flight_number or not ticket_number:
        return jsonify({"error": "Missing required fields"}), 400
    
    if flight_number == "AC123" and ticket_number == "TCK5678":
        token = create_token(flight_number, ticket_number)
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid flight or ticket"}), 401

def create_token(flight_no, ticket_no):
    payload = {
        "flight_no": flight_no,
        "ticket_no": ticket_no,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")