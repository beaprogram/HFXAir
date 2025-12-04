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


# ============== HELPER FUNCTIONS ==============

def generate_pickup_code():
    """Generate unique 6-character alphanumeric code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(6))


def generate_unique_pickup_code(cursor):
    """Generate unique pickup code that doesn't exist in database"""
    for _ in range(100):  # Max 100 attempts
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
    if stock_quantity <= 0:
        return 'out_of_stock'
    elif stock_quantity <= 5:
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
        cur.execute("SELECT ticket_id FROM tickets WHERE ticket_number = %s", (ticket_no,))
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
                b.selected_variants,
                b.created_at,
                b.expires_at,
                b.cancelled_at,
                b.picked_up_at,
                i.name as item_name,
                i.description as item_description,
                i.base_price as item_base_price,
                i.availability as item_availability,
                i.stock_quantity as item_stock_quantity,
                s.name as shop_name,
                s.location_description as shop_location,
                s.terminal as shop_terminal,
                s.gate as shop_gate
            FROM bookings b
            JOIN items i ON b.item_id = i.item_id
            JOIN shops s ON b.shop_id = s.shop_id
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
            bookings.append({
                'id': row[0],
                'user_id': row[1],
                'item_id': row[2],
                'shop_id': row[3],
                'quantity': row[4],
                'total_price': float(row[5]) if row[5] else 0.0,
                'status': row[6],
                'pickup_code': row[7],
                'selected_variants': row[8],
                'created_at': row[9].strftime('%Y-%m-%dT%H:%M:%SZ') if row[9] else None,
                'expires_at': row[10].strftime('%Y-%m-%dT%H:%M:%SZ') if row[10] else None,
                'cancelled_at': row[11].strftime('%Y-%m-%dT%H:%M:%SZ') if row[11] else None,
                'picked_up_at': row[12].strftime('%Y-%m-%dT%H:%M:%SZ') if row[12] else None,
                'item': {
                    'id': row[2],
                    'name': row[13],
                    'description': row[14],
                    'base_price': float(row[15]) if row[15] else 0.0,
                    'availability': row[16],
                    'stock_quantity': row[17]
                },
                'shop': {
                    'id': row[3],
                    'name': row[18],
                    'location': row[19],
                    'terminal': row[20],
                    'gate': row[21]
                }
            })
        
        cur.close()
        conn.close()
        
        return {'success': True, 'bookings': bookings}
    
    except Exception as e:
        logging.error(f"Error fetching bookings: {e}")
        return {'success': False, 'error': str(e)}


def create_booking(user_id, item_id, shop_id, quantity, selected_variants=None):
    """Create a new booking"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Validate quantity
        if quantity < 1 or quantity > 3:
            return {
                'success': False,
                'error': 'Invalid quantity',
                'message': 'Quantity must be between 1 and 3'
            }
        
        # Get item with lock
        cur.execute(
            "SELECT item_id, name, description, base_price, stock_quantity, availability, shop_id FROM items WHERE item_id = %s FOR UPDATE",
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
            return {'success': False, 'error': 'Invalid shop', 'message': 'Item does not belong to this shop'}
        
        # Get shop
        cur.execute("SELECT shop_id, name, location_description, terminal, gate FROM shops WHERE shop_id = %s", (shop_id,))
        shop = cur.fetchone()
        
        if not shop:
            cur.close()
            conn.close()
            return {'success': False, 'error': 'Not found', 'message': 'Shop not found'}
        
        shop_id_db, shop_name, shop_location, shop_terminal, shop_gate = shop
        
        # Check if item is out of stock
        if availability == 'out_of_stock' or stock_qty <= 0:
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
            "SELECT id FROM bookings WHERE user_id = %s AND item_id = %s AND status = 'active'",
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
        expires_at = created_at + timedelta(hours=24)
        
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
        cur.execute(
            "SELECT id, user_id, item_id, quantity, status FROM bookings WHERE id = %s FOR UPDATE",
            (booking_id,)
        )
        booking = cur.fetchone()
        
        if not booking:
            cur.close()
            conn.close()
            return {'success': False, 'error': 'Not found', 'message': 'Reservation not found'}
        
        booking_id_db, booking_user_id, item_id, quantity, status = booking
        
        # Check ownership
        if booking_user_id != user_id:
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Forbidden',
                'message': "You don't have permission to cancel this reservation"
            }
        
        # Check status
        if status == 'cancelled':
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Already cancelled',
                'message': 'This reservation has already been cancelled'
            }
        
        if status == 'expired':
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Expired',
                'message': 'This reservation has already expired'
            }
        
        if status == 'picked_up':
            cur.close()
            conn.close()
            return {
                'success': False,
                'error': 'Already picked up',
                'message': 'This item has already been picked up'
            }
        
        cancelled_at = datetime.utcnow()
        
        # Update booking
        cur.execute(
            "UPDATE bookings SET status = 'cancelled', cancelled_at = %s WHERE id = %s",
            (cancelled_at, booking_id)
        )
        
        # Restore stock
        cur.execute(
            "SELECT stock_quantity, name FROM items WHERE item_id = %s FOR UPDATE",
            (item_id,)
        )
        item = cur.fetchone()
        
        new_stock = item[0] + quantity
        new_availability = get_availability_status(new_stock)
        
        cur.execute(
            "UPDATE items SET stock_quantity = %s, availability = %s WHERE item_id = %s",
            (new_stock, new_availability, item_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'success': True,
            'booking': {
                'id': booking_id,
                'status': 'cancelled',
                'cancelled_at': cancelled_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'message': 'Reservation cancelled successfully',
                'item': {
                    'id': item_id,
                    'name': item[1],
                    'availability': new_availability,
                    'stock_quantity': new_stock
                }
            }
        }
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logging.error(f"Error cancelling booking: {e}")
        return {'success': False, 'error': str(e)}


def expire_old_bookings():
    """Expire bookings older than 24 hours"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Find expired bookings
        cur.execute("""
            SELECT id, item_id, quantity FROM bookings 
            WHERE status = 'active' AND expires_at < NOW()
        """)
        expired_bookings = cur.fetchall()
        
        count = 0
        for booking_id, item_id, quantity in expired_bookings:
            # Update status
            cur.execute(
                "UPDATE bookings SET status = 'expired' WHERE id = %s",
                (booking_id,)
            )
            
            # Restore stock
            cur.execute(
                "SELECT stock_quantity FROM items WHERE item_id = %s FOR UPDATE",
                (item_id,)
            )
            item = cur.fetchone()
            
            new_stock = item[0] + quantity
            new_availability = get_availability_status(new_stock)
            
            cur.execute(
                "UPDATE items SET stock_quantity = %s, availability = %s WHERE item_id = %s",
                (new_stock, new_availability, item_id)
            )
            
            count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        
        logging.info(f"Expired {count} bookings")
        return count
    
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
            return jsonify({"error": "Unauthorized", "message": error}), 401
        try:
            ticket_id = int(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user_id"}), 400
    
    status = request.args.get("status")
    result = get_user_bookings(user_id=ticket_id, status=status)
    
    if result['success']:
        return jsonify({'bookings': result['bookings']}), 200
    else:
        return jsonify({'error': result['error']}), 500


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
            return jsonify({"error": "Unauthorized", "message": error}), 401
        ticket_id = user_id
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    item_id = data.get('item_id')
    shop_id = data.get('shop_id')
    quantity = data.get('quantity', 1)
    selected_variants = data.get('selected_variants')
    
    if not item_id or not shop_id:
        return jsonify({"error": "Missing required fields", "message": "item_id and shop_id are required"}), 400
    
    result = create_booking(
        user_id=ticket_id,
        item_id=item_id,
        shop_id=shop_id,
        quantity=quantity,
        selected_variants=selected_variants
    )
    
    if result['success']:
        return jsonify(result['booking']), 201
    else:
        status_code = 400
        if result['error'] == 'Not found':
            status_code = 404
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
            return jsonify({"error": "Unauthorized", "message": error}), 401
        ticket_id = user_id
    
    result = cancel_booking(booking_id=booking_id, user_id=ticket_id)
    
    if result['success']:
        return jsonify(result['booking']), 200
    else:
        status_code = 400
        if result['error'] == 'Not found':
            status_code = 404
        elif result['error'] == 'Forbidden':
            status_code = 403
        return jsonify(result), status_code