# app.py
from flask import Flask, request, jsonify
app = Flask(__name__)


# login route
@app.post("/login")
def login():
    data = request.json
    if data["flight_number"] == "AC123" and data["ticket_number"] == "TCK5678":
        return jsonify({"token": "fake_token"}), 200
    return jsonify({"error": "Invalid flight or ticket"}), 401