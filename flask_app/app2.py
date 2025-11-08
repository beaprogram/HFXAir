# from flask import Flask, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from dotenv import load_dotenv
# import os

# load_dotenv()

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# db = SQLAlchemy(app)

# # Example model
# class Flight(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     flight_no = db.Column(db.String(10), nullable=False)
#     destination = db.Column(db.String(50), nullable=False)

# @app.route('/')
# def home():
#     return jsonify({"message": "Flask-Postgres API running"})

# if __name__ == '__main__':
#     app.run(debug=True)
