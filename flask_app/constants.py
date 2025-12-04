"""
Constants for Flask App - Eliminates Magic Numbers

This file contains all constants used throughout the application
to replace hardcoded "magic numbers" for better maintainability.

Usage:
    from constants import HTTP_OK, HTTP_BAD_REQUEST, MAX_BOOKING_QUANTITY
    return jsonify(data), HTTP_OK
"""

# =============================================================================
# HTTP Status Codes
# =============================================================================

# Success codes (2xx)
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204

# Client error codes (4xx)
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422

# Server error codes (5xx)
HTTP_INTERNAL_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503

# =============================================================================
# Authentication & Security
# =============================================================================

# JWT Token
TOKEN_EXPIRY_HOURS = 24  # Hours until JWT token expires

# Database Connection
DB_CONNECT_TIMEOUT_SECONDS = 5  # Timeout for database connections

# =============================================================================
# Booking Constants
# =============================================================================

# Quantity limits
MIN_BOOKING_QUANTITY = 1  # Minimum items per booking
MAX_BOOKING_QUANTITY = 3  # Maximum items per booking

# Pickup code
PICKUP_CODE_LENGTH = 6  # Length of generated pickup codes
PICKUP_CODE_MAX_ATTEMPTS = 100  # Max attempts to generate unique code

# Stock thresholds
LOW_STOCK_THRESHOLD = 5  # Items at or below this = "low stock"
OUT_OF_STOCK_THRESHOLD = 0  # Items at or below this = "out of stock"

# Booking expiry
BOOKING_EXPIRY_HOURS = 24  # Hours until booking expires

# =============================================================================
# Notification Constants
# =============================================================================

# Firebase/FCM batch sizes
FCM_BATCH_SIZE = 500  # Max FCM messages per batch
EXPO_BATCH_SIZE = 100  # Max Expo messages per request

# HTTP timeout
NOTIFICATION_HTTP_TIMEOUT_SECONDS = 10  # Timeout for notification requests

# =============================================================================
# Time & Scheduling Constants (for cron jobs)
# =============================================================================

# Reminder intervals (minutes before departure)
REMINDER_INTERVAL_EARLY = 30  # First reminder: 30 minutes before
REMINDER_INTERVAL_MIDDLE = 15  # Second reminder: 15 minutes before
REMINDER_INTERVAL_FINAL = 5  # Final reminder: 5 minutes before

# Reminder time windows (tolerance in minutes)
REMINDER_WINDOW_EARLY_MIN = 29  # 30-min reminder window start
REMINDER_WINDOW_EARLY_MAX = 31  # 30-min reminder window end
REMINDER_WINDOW_MIDDLE_MIN = 14  # 15-min reminder window start
REMINDER_WINDOW_MIDDLE_MAX = 16  # 15-min reminder window end
REMINDER_WINDOW_FINAL_MIN = 4  # 5-min reminder window start
REMINDER_WINDOW_FINAL_MAX = 6  # 5-min reminder window end

# Flight cleanup threshold
FLIGHT_CLEANUP_MINUTES = -5  # Remove from cache if past this time

# Scheduler intervals
SCHEDULER_CHECK_INTERVAL_MINUTES = 1  # How often to run cron jobs

# =============================================================================
# Date/Time Constants
# =============================================================================

# Days in months (for date calculations)
DAYS_IN_FEB_LEAP = 29
DAYS_IN_FEB_NORMAL = 28
DAYS_IN_MONTH_30 = 30
DAYS_IN_MONTH_31 = 31

# =============================================================================
# Error Messages (Optional - for consistency)
# =============================================================================

# Authentication errors
ERROR_MISSING_TOKEN = "Missing token"
ERROR_TOKEN_EXPIRED = "Token expired"
ERROR_INVALID_TOKEN = "Invalid token"
ERROR_UNAUTHORIZED = "Unauthorized"

# General errors
ERROR_BAD_REQUEST = "Bad request"
ERROR_NOT_FOUND = "Resource not found"
ERROR_INTERNAL = "Internal server error"
ERROR_MISSING_FIELDS = "Missing required fields"

# Booking errors
ERROR_INVALID_QUANTITY = "Invalid quantity"
ERROR_OUT_OF_STOCK = "Out of stock"
ERROR_INSUFFICIENT_STOCK = "Insufficient stock"
ERROR_ALREADY_RESERVED = "Already reserved"
ERROR_BOOKING_NOT_FOUND = "Booking not found"
ERROR_NOT_OWNER = "Not booking owner"
ERROR_INVALID_STATUS = "Invalid booking status"

# Shop errors
ERROR_SHOP_NOT_FOUND = "Shop not found"
ERROR_ITEM_NOT_FOUND = "Item not found"
ERROR_INVALID_PRICE_RANGE = "Invalid price range"

# Success messages
SUCCESS_CREATED = "Successfully created"
SUCCESS_UPDATED = "Successfully updated"
SUCCESS_DELETED = "Successfully deleted"
SUCCESS_SUBSCRIBED = "Subscribed"

# =============================================================================
# Application Constants
# =============================================================================

# Default values
DEFAULT_QUANTITY = 1  # Default booking quantity if not specified

# =============================================================================
# Example Usage
# =============================================================================

"""
BEFORE REFACTORING:
    return jsonify({"error": "Unauthorized"}), 401
    if quantity < 1 or quantity > 3:
        return {"error": "Invalid quantity"}
    if stock <= 5:
        status = "low_stock"

AFTER REFACTORING:
    from constants import HTTP_UNAUTHORIZED, MIN_BOOKING_QUANTITY, MAX_BOOKING_QUANTITY, LOW_STOCK_THRESHOLD
    
    return jsonify({"error": ERROR_UNAUTHORIZED}), HTTP_UNAUTHORIZED
    if quantity < MIN_BOOKING_QUANTITY or quantity > MAX_BOOKING_QUANTITY:
        return {"error": ERROR_INVALID_QUANTITY}
    if stock <= LOW_STOCK_THRESHOLD:
        status = "low_stock"
"""