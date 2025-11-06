# app.py
from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
app = Flask(__name__)
SECRET = "hfxair-app-secret"


# login route
@app.post("/login")
def login():
    data = request.json
    if data["flight_number"] == "AC123" and data["ticket_number"] == "TCK5678":
        payload = {
            "flight_no": data["flight_number"],
            "ticket_no": data["ticket_number"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET, algorithm="HS256")
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid flight or ticket"}), 401
