# auth.py
from functools import wraps
from flask import request, jsonify
import jwt

from flask_app.constants import HTTP_UNAUTHORIZED


def require_auth(secret_key):
    """
    Authentication middleware decorator.
    Validates JWT token from Authorization header.
    
    Args:
        secret_key: The secret key used to decode JWT tokens
    
    Usage:
        @app.get("/protected")
        @require_auth(SECRET)
        def protected_route():
            return jsonify({"message": "Access granted"}), 200
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing token"}), HTTP_UNAUTHORIZED

            token = auth_header.split(" ")[1]
            try:
                decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
                request.user = decoded
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), HTTP_UNAUTHORIZED
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), HTTP_UNAUTHORIZED

            return f(*args, **kwargs)
        return wrapper
    return decorator

