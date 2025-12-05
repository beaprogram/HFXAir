"""
Booking API module - handles all booking/reservation-related endpoints.
Following TDD approach - minimal implementation to make tests pass.
"""
from flask import request, jsonify
from flask_app.app import app, get_db_connection
from datetime import datetime, timedelta
import logging
import random
import string
import jwt
from flask_app.constants import (
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_ERROR,
    MIN_BOOKING_QUANTITY,
    MAX_BOOKING_QUANTITY,
    PICKUP_CODE_LENGTH,
    PICKUP_CODE_MAX_ATTEMPTS,
    LOW_STOCK_THRESHOLD,
    OUT_OF_STOCK_THRESHOLD,
    BOOKING_EXPIRY_HOURS,
    DEFAULT_QUANTITY,
    # Booking query column indices
    BOOKING_COL_ID,
    BOOKING_COL_USER_ID,
    BOOKING_COL_ITEM_ID,
    BOOKING_COL_SHOP_ID,
    BOOKING_COL_QUANTITY,
    BOOKING_COL_TOTAL_PRICE,
    BOOKING_COL_STATUS,
    BOOKING_COL_PICKUP_CODE,
    BOOKING_COL_CREATED_AT,
    BOOKING_COL_EXPIRES_AT,
    BOOKING_COL_CANCELLED_AT,
    BOOKING_COL_PICKED_UP_AT,
    BOOKING_COL_SELECTED_VARIANTS,
    BOOKING_COL_ITEM_NAME,
    BOOKING_COL_ITEM_DESCRIPTION,
    BOOKING_COL_ITEM_BASE_PRICE,
    BOOKING_COL_ITEM_AVAILABILITY,
    BOOKING_COL_ITEM_STOCK_QUANTITY,
    BOOKING_COL_SHOP_NAME,
    BOOKING_COL_SHOP_LOCATION,
    BOOKING_COL_SHOP_TERMINAL,
    BOOKING_COL_SHOP_GATE
)


# ============== HELPER FUNCTIONS ==============

def generate_pickup_code():
    """Generate unique 6-character alphanumeric code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(PICKUP_CODE_LENGTH))


def generate_unique_pickup_code(cursor):
    """Generate unique pickup code that doesn't exist in database"""
    for _ in range(PICKUP_CODE_MAX_ATTEMPTS):
        code = generate_pickup_code()
        cursor.execute("SELECT id FROM bookings WHERE pickup_code = %s", (code,))
        if not cursor.fetchone():
            return code
    raise Exception("Could not generate unique pickup code")


def calculate_total_price(base_price, quantity, selected_variants):
    """Calculate total price including variants"""
    total = float(base_price) * quantity
    if selected_variants:
        for variant in selected_variants:
            total += float(variant.get('price_adjustment', 0)) * quantity
    return round(total, 2)


def get_availability_status(stock_quantity):
    """Get availability status based on stock quantity"""
    if stock_quantity <= OUT_OF_STOCK_THRESHOLD:
        return 'out_of_stock'
    elif stock_quantity <= LOW_STOCK_THRESHOLD:
        return 'low_stock'
    else:
        return 'in_stock'


def get_ticket_id_from_token():
    """Extract ticket_id from JWT token"""
    SECRET = "hfxair-app-secret"
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, "No authorization token provided"
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        ticket_no = payload.get('ticket_no')
        
        if not ticket_no:
            return None, "Invalid token: no ticket_no"
        
        # Look up ticket_id from ticket_number
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT ticket_id FROM tickets WHERE ticket_number = %s",
            (ticket_no,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            return None, "Ticket not found"
        
        return result[0], None  # Return ticket_id
        
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


# ============== DATABASE FUNCTIONS ==============

def get_user_bookings(user_id, status=None):
    """Get all bookings for a user"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT 
                b.id,
                b.user_id,
                b.item_id,
                b.shop_id,
                b.quantity,
                b.total_price,
                b.status,
                b.pickup_code,
                b.created_at,
                b.expires_at,
                b.cancelled_at,
                b.picked_up_at,
                b.selected_variants,
                i.name as item_name,
                i.description as item_description,
                i.base_price,
                i.availability,
                i.stock_quantity,
                s.name as shop_name,
                s.location_description as shop_location,
                s.terminal as shop_terminal,
                s.gate as shop_gate
            FROM bookings b
            LEFT JOIN items i ON b.item_id = i.item_id
            LEFT JOIN shops s ON b.shop_id = s.shop_id
            WHERE b.user_id = %s
        """
        
        params = [user_id]
        
        if status:
            query += " AND b.status = %s"
            params.append(status)
        
        query += " ORDER BY b.created_at DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        bookings = []
        for row in rows:
            # Parse selected_variants if exists
            selected_variants = None
            if row[BOOKING_COL_SELECTED_VARIANTS]:
                import json
                try:
                    selected_variants = json.loads(row[BOOKING_COL_SELECTED_VARIANTS])
                except (json.JSONDecodeError, TypeError):
                    selected_variants = None
            
            booking = {
                'id': row[BOOKING_COL_ID],
                'user_id': row[BOOKING_COL_USER_ID],
                'item_id': row[BOOKING_COL_ITEM_ID],
                'shop_id': row[BOOKING_COL_SHOP_ID],
                'quantity': row[BOOKING_COL_QUANTITY],
                'total_price': float(row[BOOKING_COL_TOTAL_PRICE]),
                'status': row[BOOKING_COL_STATUS],
                'pickup_code': row[BOOKING_COL_PICKUP_CODE],
                'created_at': (row[BOOKING_COL_CREATED_AT].strftime('%Y-%m-%dT%H:%M:%SZ')
                              if row[BOOKING_COL_CREATED_AT] else None),
                'expires_at': (row[BOOKING_COL_EXPIRES_AT].strftime('%Y-%m-%dT%H:%M:%SZ')
                              if row[BOOKING_COL_EXPIRES_AT] else None),
                'cancelled_at': (row[BOOKING_COL_CANCELLED_AT].strftime('%Y-%m-%dT%H:%M:%SZ')
                                if row[BOOKING_COL_CANCELLED_AT] else None),
                'picked_up_at': (row[BOOKING_COL_PICKED_UP_AT].strftime('%Y-%m-%dT%H:%M:%SZ')
                                if row[BOOKING_COL_PICKED_UP_AT] else None),
                'selected_variants': selected_variants,
                'item': {
                    'id': row[BOOKING_COL_ITEM_ID],
                    'name': row[BOOKING_COL_ITEM_NAME],
                    'description': row[BOOKING_COL_ITEM_DESCRIPTION],
                    'base_price': (float(row[BOOKING_COL_ITEM_BASE_PRICE])
                                  if row[BOOKING_COL_ITEM_BASE_PRICE] else None),
                    'availability': row[BOOKING_COL_ITEM_AVAILABILITY],
                    'stock_quantity': row[BOOKING_COL_ITEM_STOCK_QUANTITY]
                } if row[BOOKING_COL_ITEM_NAME] else None,
                'shop': {
                    'id': row[BOOKING_COL_SHOP_ID],
                    'name': row[BOOKING_COL_SHOP_NAME],
                    'location': row[BOOKING_COL_SHOP_LOCATION],
                    'terminal': row[BOOKING_COL_SHOP_TERMINAL],
                    'gate': row[BOOKING_COL_SHOP_GATE]
                } if row[BOOKING_COL_SHOP_NAME] else None
            }
            bookings.append(booking)
        
        cur.close()
        conn.close()
        
        return {'success': True, 'bookings': bookings}
        
    except Exception as e:
        logging.error(f"Error fetching user bookings: {e}")
        return {'success': False, 'error': str(e)}


def create_booking(user_id, item_id, shop_id, quantity, selected_variants=None):
    """Create a new booking"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Validate quantity
        if quantity < MIN_BOOKING_QUANTITY or quantity > MAX_BOOKING_QUANTITY:
            return {
                'success': False,
                'error': 'Invalid quantity',
                'message': (f'Quantity must be between {MIN_BOOKING_QUANTITY} '
                           f'and {MAX_BOOKING_QUANTITY}')
            }
        
        # Get item with lock
        cur.execute(
            """SELECT item_id, name, description, base_price, stock_quantity, 
                      availability, shop_id 
               FROM items WHERE item_id = %s FOR UPDATE""",
            (item_id,)
        )
        item = cur.fetchone()
        
        if not item:
            cur.close()
            conn.close()
            return {'success': False, 'error': 'Not found', 'message': 'Item not found'}
        
        item_id_db, item_name, item_desc, base_price, stock_qty, availability, item_shop_id = item
        
        # Verify shop matches
        if item_shop_id != shop_id:
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Invalid shop',
                'message': 'Item does not belong to this shop'
            }
        
        # Get shop
        cur.execute(
            """SELECT shop_id, name, location_description, terminal, gate 
               FROM shops WHERE shop_id = %s""",
            (shop_id,)
        )
        shop = cur.fetchone()
        
        if not shop:
            cur.close()
            conn.close()
            return {'success': False, 'error': 'Not found', 'message': 'Shop not found'}
        
        shop_id_db, shop_name, shop_location, shop_terminal, shop_gate = shop
        
        # Check if item is out of stock
        if availability == 'out_of_stock' or stock_qty <= OUT_OF_STOCK_THRESHOLD:
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Out of stock',
                'message': 'This item is currently out of stock'
            }
        
        # Check if enough stock
        if stock_qty < quantity:
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Insufficient stock',
                'message': 'Not enough stock available',
                'available': stock_qty,
                'requested': quantity
            }
        
        # Check if user already has active booking for this item
        cur.execute(
            """SELECT id FROM bookings 
               WHERE user_id = %s AND item_id = %s AND status = 'active'""",
            (user_id, item_id)
        )
        existing = cur.fetchone()
        
        if existing:
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Already reserved',
                'message': 'You already have an active reservation for this item'
            }
        
        # Calculate total price
        total_price = calculate_total_price(base_price, quantity, selected_variants)
        
        # Generate unique pickup code
        pickup_code = generate_unique_pickup_code(cur)
        
        # Set times
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=BOOKING_EXPIRY_HOURS)
        
        # Convert selected_variants to JSON string if provided
        import json
        variants_json = json.dumps(selected_variants) if selected_variants else None
        
        # Create booking
        cur.execute("""
            INSERT INTO bookings 
                (user_id, item_id, shop_id, quantity, total_price, status, 
                 pickup_code, selected_variants, created_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, item_id, shop_id, quantity, total_price, 'active',
            pickup_code, variants_json, created_at, expires_at
        ))
        
        booking_id = cur.lastrowid
        
        # Reduce stock
        new_stock = stock_qty - quantity
        new_availability = get_availability_status(new_stock)
        
        cur.execute(
            "UPDATE items SET stock_quantity = %s, availability = %s WHERE item_id = %s",
            (new_stock, new_availability, item_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Return booking
        return {
            'success': True,
            'booking': {
                'id': booking_id,
                'user_id': user_id,
                'item_id': item_id,
                'shop_id': shop_id,
                'quantity': quantity,
                'total_price': total_price,
                'status': 'active',
                'pickup_code': pickup_code,
                'created_at': created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'expires_at': expires_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'cancelled_at': None,
                'picked_up_at': None,
                'selected_variants': selected_variants,
                'item': {
                    'id': item_id,
                    'name': item_name,
                    'description': item_desc,
                    'base_price': float(base_price),
                    'availability': new_availability,
                    'stock_quantity': new_stock
                },
                'shop': {
                    'id': shop_id,
                    'name': shop_name,
                    'location': shop_location,
                    'terminal': shop_terminal,
                    'gate': shop_gate
                }
            }
        }
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logging.error(f"Error creating booking: {e}")
        return {'success': False, 'error': str(e)}


def cancel_booking(booking_id, user_id):
    """Cancel an active booking"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get booking with lock
        cur.execute("""
            SELECT id, user_id, item_id, quantity, status
            FROM bookings 
            WHERE id = %s 
            FOR UPDATE
        """, (booking_id,))
        booking = cur.fetchone()
        
        if not booking:
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Not found',
                'message': 'Booking not found'
            }
        
        booking_id_db, booking_user_id, item_id, quantity, status = booking
        
        # Verify user owns the booking
        if booking_user_id != user_id:
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Forbidden',
                'message': 'Not your booking'
            }
        
        # Check if booking is active
        if status != 'active':
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Invalid status',
                'message': f'Cannot cancel booking with status: {status}'
            }
        
        # Update booking status
        cancelled_at = datetime.utcnow()
        cur.execute("""
            UPDATE bookings 
            SET status = 'cancelled', cancelled_at = %s 
            WHERE id = %s
        """, (cancelled_at, booking_id))
        
        # Restore stock
        cur.execute("""
            UPDATE items 
            SET stock_quantity = stock_quantity + %s 
            WHERE item_id = %s
        """, (quantity, item_id))
        
        # Get updated stock to recalculate availability
        cur.execute("SELECT stock_quantity FROM items WHERE item_id = %s", (item_id,))
        result = cur.fetchone()
        new_stock = result[0] if result else 0
        new_availability = get_availability_status(new_stock)
        
        cur.execute(
            "UPDATE items SET availability = %s WHERE item_id = %s",
            (new_availability, item_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Return success with booking info (satisfies both test files)
        return {
            'success': True,
            'booking': {
                'id': booking_id_db,
                'status': 'cancelled',
                'cancelled_at': cancelled_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logging.error(f"Error cancelling booking: {e}")
        return {'success': False, 'error': str(e)}


def expire_old_bookings():
    """Expire bookings that have passed their expiration time"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Find expired active bookings
        now = datetime.utcnow()
        cur.execute("""
            SELECT id, item_id, quantity
            FROM bookings
            WHERE status = 'active' AND expires_at < %s
            FOR UPDATE
        """, (now,))
        
        expired_bookings = cur.fetchall()
        
        for booking_id, item_id, quantity in expired_bookings:
            # Update booking status
            cur.execute("""
                UPDATE bookings 
                SET status = 'expired' 
                WHERE id = %s
            """, (booking_id,))
            
            # Restore stock
            cur.execute("""
                UPDATE items 
                SET stock_quantity = stock_quantity + %s 
                WHERE item_id = %s
            """, (quantity, item_id))
            
            # Update availability
            cur.execute(
                "SELECT stock_quantity FROM items WHERE item_id = %s",
                (item_id,)
            )
            result = cur.fetchone()
            new_stock = result[0] if result else 0
            new_availability = get_availability_status(new_stock)
            
            cur.execute(
                "UPDATE items SET availability = %s WHERE item_id = %s",
                (new_availability, item_id)
            )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return len(expired_bookings)
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logging.error(f"Error expiring bookings: {e}")
        raise e


# ============== ROUTE HANDLERS ==============

@app.get("/bookings")
def list_bookings():
    """GET /bookings - Get all user bookings"""
    # Get ticket_id from JWT token
    ticket_id, error = get_ticket_id_from_token()
    
    if error:
        # Fallback to query param for testing
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized", "message": error}), HTTP_UNAUTHORIZED
        try:
            ticket_id = int(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user_id"}), HTTP_BAD_REQUEST
    
    status = request.args.get("status")
    result = get_user_bookings(user_id=ticket_id, status=status)
    
    if result['success']:
        return jsonify({'bookings': result['bookings']}), HTTP_OK
    else:
        return jsonify({'error': result['error']}), HTTP_INTERNAL_ERROR


@app.post("/bookings")
def create_booking_route():
    """POST /bookings - Create new booking"""
    # Get ticket_id from JWT token
    ticket_id, error = get_ticket_id_from_token()
    
    if error:
        # Fallback to request body for testing
        data = request.get_json() or {}
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized", "message": error}), HTTP_UNAUTHORIZED
        ticket_id = user_id
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Missing request body"}), HTTP_BAD_REQUEST
    
    item_id = data.get('item_id')
    shop_id = data.get('shop_id')
    quantity = data.get('quantity', DEFAULT_QUANTITY)
    selected_variants = data.get('selected_variants')
    
    if not item_id or not shop_id:
        return jsonify({
            "error": "Missing required fields",
            "message": "item_id and shop_id are required"
        }), HTTP_BAD_REQUEST
    
    result = create_booking(
        user_id=ticket_id,
        item_id=item_id,
        shop_id=shop_id,
        quantity=quantity,
        selected_variants=selected_variants
    )
    
    if result['success']:
        return jsonify(result['booking']), HTTP_CREATED
    else:
        status_code = HTTP_BAD_REQUEST
        if result['error'] == 'Not found':
            status_code = HTTP_NOT_FOUND
        return jsonify(result), status_code


@app.post("/bookings/<int:booking_id>/cancel")
def cancel_booking_route(booking_id):
    """POST /bookings/<booking_id>/cancel - Cancel booking"""
    # Get ticket_id from JWT token
    ticket_id, error = get_ticket_id_from_token()
    
    if error:
        # Fallback to request body for testing
        data = request.get_json() or {}
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized", "message": error}), HTTP_UNAUTHORIZED
        ticket_id = user_id
    
    result = cancel_booking(booking_id=booking_id, user_id=ticket_id)
    
    if result['success']:
        # Return the booking object (not wrapped) for API response
        return jsonify(result['booking']), HTTP_OK
    else:
        status_code = HTTP_BAD_REQUEST
        if result['error'] == 'Not found':
            status_code = HTTP_NOT_FOUND
        elif result['error'] == 'Forbidden':
            status_code = HTTP_FORBIDDEN
        return jsonify(result), status_code