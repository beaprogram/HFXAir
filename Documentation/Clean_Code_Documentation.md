# Clean Code Practices Documentation

---

## Overview

This document demonstrates adherence to traditional clean code practices throughout the HFXAIR backend codebase.

---

## 1. Small, Focused Methods

Each function performs a single, well-defined task following the Single Responsibility Principle (SRP).

### Example 1: Helper Functions in `booking.py`

```python
def generate_pickup_code():
    """Generate unique 6-character alphanumeric code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(6))


def calculate_total_price(base_price, quantity, selected_variants):
    """Calculate total price including variants"""
    total = float(base_price) * quantity
    if selected_variants:
        for variant in selected_variants:
            total += float(variant.get('price_adjustment', 0)) * quantity
    return round(total, 2)


def get_availability_status(stock_quantity):
    """Get availability status based on stock quantity"""
    if stock_quantity <= 0:
        return 'out_of_stock'
    elif stock_quantity <= 5:
        return 'low_stock'
    else:
        return 'in_stock'
```

**Why this is clean:**
- Each function is < 10 lines
- Single responsibility (generate code, calculate price, determine status)
- Descriptive names indicate purpose
- No side effects

### Example 2: Authentication Decorator in `auth.py`

```python
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
                return jsonify({"error": "Missing token"}), 401

            token = auth_header.split(" ")[1]
            try:
                decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
                request.user = decoded
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

            return f(*args, **kwargs)
        return wrapper
    return decorator
```

**Why this is clean:**
- Reusable authentication logic
- Clear error handling for each failure case
- Comprehensive docstring with usage example
- Follows decorator pattern correctly

---

## 2. Comments Explaining WHY (Not What)

Our comments explain rationale and business logic, not obvious code behavior.

### Example 1: Database Locking Rationale

```python
# Get item with lock - prevents race conditions during concurrent bookings
cur.execute(
    "SELECT item_id, name, description, base_price, stock_quantity, availability, shop_id "
    "FROM items WHERE item_id = %s FOR UPDATE",
    (item_id,)
)
```

### Example 2: Business Rule Comments

```python
# Validate quantity - business rule limits reservations to prevent hoarding
if quantity < 1 or quantity > 3:
    return {
        'success': False,
        'error': 'Invalid quantity',
        'message': 'Quantity must be between 1 and 3'
    }
```

### Example 3: Fallback Logic Explanation

```python
# Get ticket_id from JWT token
ticket_id, error = get_ticket_id_from_token()

if error:
    # Fallback to query param for testing - allows unit tests without JWT setup
    user_id = request.args.get("user_id")
```

### Example 4: Time Handling Rationale

```python
# Halifax timezone - all shop hours are displayed in local time
HALIFAX_TZ = pytz.timezone('America/Halifax')

# Get current day of week (0=Monday, 6=Sunday) - matches database schema
current_day = datetime.now(HALIFAX_TZ).weekday()
```

### Example 5: Stock Restoration Logic

```python
# Restore stock - cancelled items become available for other customers
cur.execute(
    "SELECT stock_quantity, name FROM items WHERE item_id = %s FOR UPDATE",
    (item_id,)
)
item = cur.fetchone()

new_stock = item[0] + quantity
new_availability = get_availability_status(new_stock)
```

---

## 3. No Double Negatives in Conditions

All conditions are written in positive, readable form.

### Good Examples (Our Code)

```python
# Positive condition - easy to understand
if not is_closed and open_t and close_t:
    is_open = open_time <= current_time <= close_time

# Direct status check
if status == 'cancelled':
    return {'error': 'Already cancelled'}

# Clear null check
if not item:
    return {'error': 'Not found', 'message': 'Item not found'}

# Simple boolean check
if open_now and not is_open:
    continue  # Skip closed shops when filtering for open ones
```

### Avoided Patterns

```python
# Double negative (NOT in our code)
if not is_not_closed:  # Confusing!

# Our approach
if not is_closed:  # Clear and readable
```

---

## 4. Named Constants (No Magic Numbers)

All magic numbers have been extracted to named constants with clear meaning.

### Example 1: Pickup Code Configuration

```python
# Constants define pickup code format
PICKUP_CODE_LENGTH = 6
PICKUP_CODE_CHARS = string.ascii_uppercase + string.digits

def generate_pickup_code():
    """Generate unique 6-character alphanumeric code"""
    return ''.join(random.choice(PICKUP_CODE_CHARS) for _ in range(PICKUP_CODE_LENGTH))
```

### Example 2: Stock Thresholds

```python
LOW_STOCK_THRESHOLD = 5

def get_availability_status(stock_quantity):
    """Get availability status based on stock quantity"""
    if stock_quantity <= 0:
        return 'out_of_stock'
    elif stock_quantity <= LOW_STOCK_THRESHOLD:
        return 'low_stock'
    else:
        return 'in_stock'
```

### Example 3: Business Rule Constants

```python
MIN_BOOKING_QUANTITY = 1
MAX_BOOKING_QUANTITY = 3
BOOKING_EXPIRY_HOURS = 24
MAX_PICKUP_CODE_ATTEMPTS = 100

# Validate quantity
if quantity < MIN_BOOKING_QUANTITY or quantity > MAX_BOOKING_QUANTITY:
    return {
        'success': False,
        'error': 'Invalid quantity',
        'message': f'Quantity must be between {MIN_BOOKING_QUANTITY} and {MAX_BOOKING_QUANTITY}'
    }
```

### Example 4: Timezone Configuration

```python
# Named constant for timezone - used throughout shop hours calculations
HALIFAX_TZ = pytz.timezone('America/Halifax')
```

### Refactoring Evidence (Git Commits)

```
f398f006 - refactor: eliminate magic numbers and fix code smells from DPy analysis
6b4e2852 - removing magic numbers from all possible files
a6e890aa - changing test files for removing magic numbers
```

---

## 5. Meaningful Names

### Variables

```python
# Descriptive variable names
booking_user_id = booking[1]      # Not: bu or bid
stock_quantity = item[4]          # Not: sq or s
shop_location = row[19]           # Not: loc or l
current_time = datetime.now(HALIFAX_TZ).time()  # Not: t or ct

# Clear unpacking with meaningful names
item_id_db, item_name, item_desc, base_price, stock_qty, availability, item_shop_id = item
shop_id_db, shop_name, shop_location, shop_terminal, shop_gate = shop
```

### Functions

```python
# Verb-noun naming pattern
def generate_pickup_code():       # Not: code() or gen_code()
def calculate_total_price():      # Not: calc() or price()
def get_availability_status():    # Not: status() or avail()
def cancel_booking():             # Not: cancel() or cb()
def expire_old_bookings():        # Not: expire() or cleanup()

# Route handlers clearly named
def list_bookings():              # GET /bookings
def create_booking_route():       # POST /bookings
def cancel_booking_route():       # POST /bookings/<id>/cancel
```

### Boolean Variables

```python
# is/has prefix for booleans
is_open = False
is_closed = hours_row[2]
include_items = request.args.get("include_items", "true")
```

---

## 6. DRY Principle (Don't Repeat Yourself)

### Reusable Helper Functions

```python
# Used across multiple routes and functions
def get_availability_status(stock_quantity):
    """Centralized stock status logic - used by booking and cancellation"""
    if stock_quantity <= 0:
        return 'out_of_stock'
    elif stock_quantity <= 5:
        return 'low_stock'
    else:
        return 'in_stock'

# Called in:
# - create_booking() after decreasing stock
# - cancel_booking() after restoring stock
# - expire_old_bookings() after restoring stock
```

### Token Extraction Function

```python
def get_ticket_id_from_token():
    """
    Extract ticket_id from JWT token.
    Centralized authentication logic used by all booking endpoints.
    """
    # ... implementation
    return ticket_id, error_message

# Reused in:
# - list_bookings()
# - create_booking_route()
# - cancel_booking_route()
```

---

## 7. Proper Error Handling

### Consistent Error Response Structure

```python
# All errors follow the same structure
return {
    'success': False,
    'error': 'Error Type',           # Machine-readable error code
    'message': 'Human readable message'  # User-friendly explanation
}
```

### Specific Error Types

```python
# Not found errors
return {'success': False, 'error': 'Not found', 'message': 'Item not found'}
return {'success': False, 'error': 'Not found', 'message': 'Shop not found'}
return {'success': False, 'error': 'Not found', 'message': 'Reservation not found'}

# Authorization errors
return {'success': False, 'error': 'Forbidden', 'message': "You don't have permission..."}

# Validation errors
return {'success': False, 'error': 'Invalid quantity', 'message': 'Quantity must be between 1 and 3'}
return {'success': False, 'error': 'Out of stock', 'message': 'This item is currently out of stock'}

# State errors
return {'success': False, 'error': 'Already cancelled', 'message': 'This reservation has already been cancelled'}
return {'success': False, 'error': 'Already reserved', 'message': 'You already have an active reservation for this item'}
```

### Exception Handling with Logging

```python
try:
    conn = get_db_connection()
    # ... database operations
    conn.commit()
except Exception as e:
    if conn:
        conn.rollback()  # Ensure transaction safety
        conn.close()
    logging.error(f"Error cancelling booking: {e}")  # Log for debugging
    return {'success': False, 'error': str(e)}
```

### HTTP Status Code Mapping

```python
@app.post("/bookings")
def create_booking_route():
    result = create_booking(...)
    
    if result['success']:
        return jsonify(result['booking']), 201  # Created
    else:
        status_code = 400  # Bad Request (default)
        if result['error'] == 'Not found':
            status_code = 404  # Not Found
        elif result['error'] == 'Forbidden':
            status_code = 403  # Forbidden
        return jsonify(result), status_code
```

---

## 8. Code Organization

### Module Structure

```
flask_app/
├── app.py              # Main Flask app, core routes
├── auth.py             # Authentication middleware
├── booking.py          # Booking module (helpers + database + routes)
├── shop.py             # Shop module (helpers + database + routes)
└── helper/
    ├── helper_cron_jobs.py           # Background job utilities
    └── helper_firebase_notification.py  # Push notification utilities
```

### Section Headers in Modules

```python
# booking.py structure
"""
Booking API module - handles all booking/reservation-related endpoints.
Following TDD approach - minimal implementation to make tests pass.
"""

# ============== HELPER FUNCTIONS ==============
def generate_pickup_code(): ...
def calculate_total_price(): ...
def get_availability_status(): ...

# ============== DATABASE FUNCTIONS ==============
def get_user_bookings(): ...
def create_booking(): ...
def cancel_booking(): ...
def expire_old_bookings(): ...

# ============== ROUTE HANDLERS ==============
@app.get("/bookings")
def list_bookings(): ...

@app.post("/bookings")
def create_booking_route(): ...
```

---

## 9. Input Validation

### Type Conversion with Error Handling

```python
# Convert min_price to float if provided
if min_price is not None:
    try:
        min_price = float(min_price)
    except ValueError:
        min_price = None  # Graceful fallback

# Convert category_id to int if provided
if category_id is not None:
    try:
        category_id = int(category_id)
    except ValueError:
        category_id = None
```

### Range Validation

```python
# Validate price range - logical check before database query
if min_price is not None and max_price is not None:
    if min_price > max_price:
        return jsonify({
            "error": "Invalid price range: min_price cannot be greater than max_price"
        }), 400
```

### Boolean Parameter Handling

```python
# Convert string to boolean with clear logic
open_now = request.args.get("open_now")
if open_now is not None:
    open_now = open_now.lower() == "true"
```

---

## 10. Docstrings and Documentation

### Module-Level Documentation

```python
"""
Booking API module - handles all booking/reservation-related endpoints.
Following TDD approach - minimal implementation to make tests pass.
"""
```

### Function Documentation

```python
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
```

### Route Documentation

```python
@app.get("/bookings")
def list_bookings():
    """GET /bookings - Get all user bookings"""

@app.post("/bookings/<int:booking_id>/cancel")
def cancel_booking_route(booking_id):
    """POST /bookings/<booking_id>/cancel - Cancel booking"""
```

---


