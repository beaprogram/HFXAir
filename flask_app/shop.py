"""
Shop API module - handles all shop-related endpoints.
Following TDD approach - minimal implementation to make tests pass.
"""
from flask import request, jsonify
from flask_app.app import app, get_db_connection
from datetime import datetime, time, timedelta
import logging
import pytz

from flask_app.constants import (
    HTTP_OK,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND
)

# Halifax timezone
HALIFAX_TZ = pytz.timezone('America/Halifax')


def get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
    """Get shops with filtering and sorting"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if category:
            where_conditions.append("s.category = %s")
            params.append(category)
        
        if terminal:
            where_conditions.append("s.terminal = %s")
            params.append(terminal)
        
        if gate:
            where_conditions.append("s.gate = %s")
            params.append(gate)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get current day of week (0=Monday, 6=Sunday)
        current_day = datetime.now(HALIFAX_TZ).weekday()
        current_time = datetime.now(HALIFAX_TZ).time()
        
        # Build ORDER BY clause
        order_by = "ORDER BY s.name"
        if sort == "name":
            order_by = "ORDER BY s.name"
        elif sort == "gate":
            order_by = "ORDER BY s.gate"
        elif sort == "status":
            # For status sorting, we'll sort by is_open in Python after fetching
            order_by = "ORDER BY s.name"
        
        query = f"""
            SELECT 
                s.shop_id,
                s.name,
                s.category,
                s.description,
                s.terminal,
                s.gate,
                s.location_description,
                sh.open_time,
                sh.close_time,
                sh.is_closed
            FROM shops s
            LEFT JOIN shop_hours sh ON s.shop_id = sh.shop_id AND sh.day_of_week = %s
            {where_clause}
            {order_by}
        """
        
        query_params = [current_day] + params
        
        logging.info(f"Executing query: {query}")
        logging.info(f"Query params: {query_params}")
        cur.execute(query, query_params)
        rows = cur.fetchall()
        logging.info(f"Fetched {len(rows)} rows from database")
        
        shops = []
        filters_applied = {}
        
        for row in rows:
            shop_id, name, cat, desc, term, gate_val, loc, open_t, close_t, is_closed = row
            
            # Calculate is_open status
            is_open = False
            status = "Unknown"
            next_change = None
            
            if open_t and close_t and not is_closed:
                try:
                    # Handle time objects or strings
                    if isinstance(open_t, time):
                        open_time = open_t
                    else:
                        open_str = str(open_t).rstrip(':').split(':')
                        open_time = time(int(open_str[0]), int(open_str[1]))
                    
                    if isinstance(close_t, time):
                        close_time = close_t
                    else:
                        close_str = str(close_t).rstrip(':').split(':')
                        close_time = time(int(close_str[0]), int(close_str[1]))
                    
                    # Check if currently open
                    if open_time <= current_time < close_time:
                        is_open = True
                        status = "Open"
                        # Calculate next_change (closing time)
                        now = datetime.now(HALIFAX_TZ)
                        close_datetime = now.replace(hour=close_time.hour, minute=close_time.minute, second=0, microsecond=0)
                        next_change = close_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
                    else:
                        is_open = False
                        status = "Closed"
                        # Calculate next_change (opening time)
                        now = datetime.now(HALIFAX_TZ)
                        open_datetime = now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
                        
                        # If opening time is earlier than current time, it's tomorrow
                        if open_time < current_time:
                            open_datetime += timedelta(days=1)
                        
                        next_change = open_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
                    
                except Exception as e:
                    logging.error(f"Error parsing shop hours: {e}")
                    status = "Unknown"
            elif is_closed:
                status = "Closed"
            else:
                status = "Unknown"
            
            shop = {
                "id": shop_id,
                "name": name,
                "category": cat,
                "description": desc,
                "terminal": term,
                "gate": gate_val,
                "location": loc,
                "status": status,
                "is_open": is_open,
                "next_change": next_change
            }
            
            # Apply open_now filter if specified
            if open_now is not None:
                if open_now and not is_open:
                    continue
                elif not open_now and is_open:
                    continue
            
            shops.append(shop)
        
        # Sort by status if requested
        if sort == "status":
            shops.sort(key=lambda x: (not x["is_open"], x["name"]))
        
        cur.close()
        conn.close()
        
        # Track which filters were applied
        if category:
            filters_applied["category"] = category
        if open_now is not None:
            filters_applied["open_now"] = open_now
        if terminal:
            filters_applied["terminal"] = terminal
        if gate:
            filters_applied["gate"] = gate
        
        return {
            "shops": shops,
            "count": len(shops),
            "filters_applied": filters_applied
        }
        
    except Exception as e:
        logging.error(f"Error fetching shops: {e}")
        return None


def get_shop_by_id(shop_id):
    """Get detailed shop information by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get shop basic info
        cur.execute("""
            SELECT shop_id, name, category, description, terminal, gate, location_description
            FROM shops
            WHERE shop_id = %s
        """, (shop_id,))
        shop_row = cur.fetchone()
        
        if not shop_row:
            cur.close()
            conn.close()
            return None
        
        shop_id_db, name, category, description, terminal, gate, location = shop_row
        
        # Get current shop hours (for today)
        current_day = datetime.now(HALIFAX_TZ).weekday()
        current_time = datetime.now(HALIFAX_TZ).time()
        
        cur.execute("""
            SELECT open_time, close_time, is_closed
            FROM shop_hours
            WHERE shop_id = %s AND day_of_week = %s
        """, (shop_id, current_day))
        hours_row = cur.fetchone()
        
        is_open = False
        status = "Unknown"
        next_change = None
        
        if hours_row:
            open_t, close_t, is_closed = hours_row
            
            if open_t and close_t and not is_closed:
                try:
                    if isinstance(open_t, time):
                        open_time = open_t
                    else:
                        open_str = str(open_t).rstrip(':').split(':')
                        open_time = time(int(open_str[0]), int(open_str[1]))
                    
                    if isinstance(close_t, time):
                        close_time = close_t
                    else:
                        close_str = str(close_t).rstrip(':').split(':')
                        close_time = time(int(close_str[0]), int(close_str[1]))
                    
                    if open_time <= current_time < close_time:
                        is_open = True
                        status = "Open"
                        now = datetime.now(HALIFAX_TZ)
                        close_datetime = now.replace(hour=close_time.hour, minute=close_time.minute, second=0, microsecond=0)
                        next_change = close_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
                    else:
                        is_open = False
                        status = "Closed"
                        now = datetime.now(HALIFAX_TZ)
                        open_datetime = now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
                        if open_time < current_time:
                            open_datetime += timedelta(days=1)
                        next_change = open_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
                except Exception as e:
                    logging.error(f"Error parsing hours: {e}")
            elif is_closed:
                status = "Closed"
        
        cur.close()
        conn.close()
        
        return {
            "id": shop_id_db,
            "name": name,
            "category": category,
            "description": description,
            "terminal": terminal,
            "gate": gate,
            "location": location,
            "status": status,
            "is_open": is_open,
            "next_change": next_change
        }
        
    except Exception as e:
        logging.error(f"Error fetching shop by ID: {e}")
        return None


def get_shop_hours(shop_id):
    """Get weekly shop hours"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if shop exists
        cur.execute("SELECT shop_id, name FROM shops WHERE shop_id = %s", (shop_id,))
        shop_row = cur.fetchone()
        
        if not shop_row:
            cur.close()
            conn.close()
            return None
        
        shop_id_db, shop_name = shop_row
        
        # Get hours for all days
        cur.execute("""
            SELECT day_of_week, open_time, close_time, is_closed
            FROM shop_hours
            WHERE shop_id = %s
            ORDER BY day_of_week
        """, (shop_id,))
        
        hours_rows = cur.fetchall()
        
        # Day names mapping
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        weekly_hours = []
        for day_num, open_t, close_t, is_closed in hours_rows:
            day_name = day_names[day_num] if 0 <= day_num < 7 else f"Day {day_num}"
            
            if is_closed:
                weekly_hours.append({
                    "day": day_name,
                    "day_of_week": day_num,
                    "status": "Closed",
                    "open_time": None,
                    "close_time": None
                })
            else:
                open_str = str(open_t) if open_t else None
                close_str = str(close_t) if close_t else None
                
                weekly_hours.append({
                    "day": day_name,
                    "day_of_week": day_num,
                    "status": "Open",
                    "open_time": open_str,
                    "close_time": close_str
                })
        
        cur.close()
        conn.close()
        
        return {
            "shop_id": shop_id_db,
            "shop_name": shop_name,
            "hours": weekly_hours
        }
        
    except Exception as e:
        logging.error(f"Error fetching shop hours: {e}")
        return None


def get_shop_categories():
    """Get all unique shop categories"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT category 
            FROM shops 
            WHERE category IS NOT NULL 
            ORDER BY category
        """)
        
        rows = cur.fetchall()
        categories = [row[0] for row in rows]
        
        cur.close()
        conn.close()
        
        return {"categories": categories}
        
    except Exception as e:
        logging.error(f"Error fetching shop categories: {e}")
        return {"categories": []}


def get_shop_catalog(shop_id, include_items=True):
    """Get shop catalog with categories and optionally items"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if shop exists
        cur.execute("SELECT shop_id, name, description FROM shops WHERE shop_id = %s", (shop_id,))
        shop_row = cur.fetchone()
        
        if not shop_row:
            cur.close()
            conn.close()
            return None
        
        shop_id_db, shop_name, shop_desc = shop_row
        
        # Get categories for this shop
        cur.execute("""
            SELECT DISTINCT ic.category_id, ic.category_name
            FROM item_categories ic
            INNER JOIN items i ON ic.category_id = i.category_id
            WHERE i.shop_id = %s
            ORDER BY ic.category_name
        """, (shop_id,))
        
        category_rows = cur.fetchall()
        
        categories = []
        for cat_id, cat_name in category_rows:
            category = {
                "category_id": cat_id,
                "category_name": cat_name
            }
            
            if include_items:
                # Get items for this category
                cur.execute("""
                    SELECT item_id, name, description, base_price, stock_quantity, availability
                    FROM items
                    WHERE shop_id = %s AND category_id = %s
                    ORDER BY name
                """, (shop_id, cat_id))
                
                item_rows = cur.fetchall()
                items = []
                for item_id, item_name, item_desc, price, stock, avail in item_rows:
                    items.append({
                        "item_id": item_id,
                        "name": item_name,
                        "description": item_desc,
                        "base_price": float(price) if price else None,
                        "stock_quantity": stock,
                        "availability": avail
                    })
                
                category["items"] = items
                category["item_count"] = len(items)
            
            categories.append(category)
        
        cur.close()
        conn.close()
        
        return {
            "shop_id": shop_id_db,
            "shop_name": shop_name,
            "shop_description": shop_desc,
            "categories": categories
        }
        
    except Exception as e:
        logging.error(f"Error fetching shop catalog: {e}")
        return None


def get_shop_items(shop_id, search=None, category_id=None, min_price=None, max_price=None, availability=None, sort=None):
    """Get shop items with filtering and sorting"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if shop exists
        cur.execute("SELECT shop_id, name FROM shops WHERE shop_id = %s", (shop_id,))
        shop_row = cur.fetchone()
        
        if not shop_row:
            cur.close()
            conn.close()
            return None
        
        shop_id_db, shop_name = shop_row
        
        # Build WHERE clause
        where_conditions = ["i.shop_id = %s"]
        params = [shop_id]
        
        if search:
            where_conditions.append("(i.name LIKE %s OR i.description LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if category_id:
            where_conditions.append("i.category_id = %s")
            params.append(category_id)
        
        if min_price is not None:
            where_conditions.append("i.base_price >= %s")
            params.append(min_price)
        
        if max_price is not None:
            where_conditions.append("i.base_price <= %s")
            params.append(max_price)
        
        if availability:
            where_conditions.append("i.availability = %s")
            params.append(availability)
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Build ORDER BY clause
        order_by = "ORDER BY i.name"
        if sort == "price_asc":
            order_by = "ORDER BY i.base_price ASC"
        elif sort == "price_desc":
            order_by = "ORDER BY i.base_price DESC"
        elif sort == "name":
            order_by = "ORDER BY i.name"
        
        query = f"""
            SELECT 
                i.item_id,
                i.name,
                i.description,
                i.base_price,
                i.stock_quantity,
                i.availability,
                i.category_id,
                ic.category_name
            FROM items i
            LEFT JOIN item_categories ic ON i.category_id = ic.category_id
            {where_clause}
            {order_by}
        """
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        items = []
        for row in rows:
            item_id, name, desc, price, stock, avail, cat_id, cat_name = row
            items.append({
                "item_id": item_id,
                "name": name,
                "description": desc,
                "base_price": float(price) if price else None,
                "stock_quantity": stock,
                "availability": avail,
                "category": {
                    "category_id": cat_id,
                    "category_name": cat_name
                } if cat_id else None
            })
        
        cur.close()
        conn.close()
        
        return {
            "shop_id": shop_id_db,
            "shop_name": shop_name,
            "items": items,
            "count": len(items)
        }
        
    except Exception as e:
        logging.error(f"Error fetching shop items: {e}")
        return None


def get_item_by_id(item_id):
    """Get item details by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT 
                i.item_id,
                i.name,
                i.description,
                i.base_price,
                i.stock_quantity,
                i.availability,
                i.shop_id,
                i.category_id,
                s.name as shop_name,
                ic.category_name
            FROM items i
            LEFT JOIN shops s ON i.shop_id = s.shop_id
            LEFT JOIN item_categories ic ON i.category_id = ic.category_id
            WHERE i.item_id = %s
        """
        
        cur.execute(query, (item_id,))
        row = cur.fetchone()
        
        if not row:
            cur.close()
            conn.close()
            return None
        
        item_id, name, desc, price, stock, avail, shop_id, cat_id, shop_name, cat_name = row
        
        # Get variants if any
        cur.execute("""
            SELECT variant_id, variant_name, additional_price, stock_quantity
            FROM product_variants
            WHERE item_id = %s
            ORDER BY variant_name
        """, (item_id,))
        
        variant_rows = cur.fetchall()
        variants = []
        for var_id, var_name, add_price, var_stock in variant_rows:
            variants.append({
                "variant_id": var_id,
                "variant_name": var_name,
                "additional_price": float(add_price) if add_price else 0.0,
                "stock_quantity": var_stock
            })
        
        cur.close()
        conn.close()
        
        return {
            "item_id": item_id,
            "name": name,
            "description": desc,
            "base_price": float(price) if price else None,
            "stock_quantity": stock,
            "availability": avail,
            "shop": {
                "shop_id": shop_id,
                "shop_name": shop_name
            } if shop_id else None,
            "category": {
                "category_id": cat_id,
                "category_name": cat_name
            } if cat_id else None,
            "variants": variants
        }
        
    except Exception as e:
        logging.error(f"Error fetching item by ID: {e}")
        return None


def get_shop_item_categories(shop_id):
    """Get item categories for a shop"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if shop exists
        check_query = "SELECT shop_id, name FROM shops WHERE shop_id = %s"
        cur.execute(check_query, (shop_id,))
        shop_row = cur.fetchone()
        
        if not shop_row:
            cur.close()
            conn.close()
            return None
        
        shop_id_db, shop_name = shop_row
        
        # Get categories with item counts
        query = """
            SELECT ic.category_id, ic.category_name, COUNT(i.item_id) as item_count
            FROM item_categories ic
            LEFT JOIN items i ON ic.category_id = i.category_id AND i.shop_id = %s
            WHERE EXISTS (
                SELECT 1 FROM items WHERE shop_id = %s AND category_id = ic.category_id
            )
            GROUP BY ic.category_id, ic.category_name
            ORDER BY ic.category_name
        """
        cur.execute(query, (shop_id, shop_id))
        rows = cur.fetchall()
        
        categories = []
        for cat_id, cat_name, item_count in rows:
            categories.append({
                "category_id": cat_id,
                "category_name": cat_name,
                "item_count": item_count
            })
        
        cur.close()
        conn.close()
        
        return {
            "shop_id": shop_id_db,
            "shop_name": shop_name,
            "categories": categories
        }
    except Exception as e:
        logging.error(f"Error fetching shop item categories: {e}")
        return None


# Route handlers
@app.get("/shops")
def list_shops():
    """GET /shops - List all shops with filtering"""
    category = request.args.get("category")
    open_now = request.args.get("open_now")
    sort = request.args.get("sort")
    terminal = request.args.get("terminal")
    gate = request.args.get("gate")
    
    # Convert open_now string to boolean
    if open_now is not None:
        open_now = open_now.lower() == "true"
    
    result = get_shops(category=category, open_now=open_now, sort=sort, 
                      terminal=terminal, gate=gate)
    return jsonify(result), HTTP_OK


@app.get("/shops/<int:shop_id>")
def get_shop_details(shop_id):
    """GET /shops/<shop_id> - Get shop details"""
    shop = get_shop_by_id(shop_id)
    if shop is None:
        return jsonify({"error": "Shop not found"}), HTTP_NOT_FOUND
    return jsonify(shop), HTTP_OK


@app.get("/shops/<int:shop_id>/hours")
def get_shop_hours_route(shop_id):
    """GET /shops/<shop_id>/hours - Get shop hours"""
    hours = get_shop_hours(shop_id)
    if hours is None:
        return jsonify({"error": "Shop not found"}), HTTP_NOT_FOUND
    return jsonify(hours), HTTP_OK


@app.get("/shops/categories")
def list_shop_categories():
    """GET /shops/categories - Get all shop categories"""
    result = get_shop_categories()
    return jsonify(result), HTTP_OK


@app.get("/shops/<int:shop_id>/catalog")
def get_shop_catalog_route(shop_id):
    """GET /shops/<shop_id>/catalog - Get shop catalog"""
    include_items = request.args.get("include_items", "true")
    include_items = include_items.lower() == "true"
    
    catalog = get_shop_catalog(shop_id, include_items=include_items)
    if catalog is None:
        return jsonify({"error": "Shop not found"}), HTTP_NOT_FOUND
    return jsonify(catalog), HTTP_OK


@app.get("/shops/<int:shop_id>/items")
def list_shop_items(shop_id):
    """GET /shops/<shop_id>/items - Get shop items"""
    search = request.args.get("search")
    category_id = request.args.get("category_id")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    availability = request.args.get("availability")
    sort = request.args.get("sort")
    
    # Convert min_price to float if provided
    if min_price is not None:
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = None
    
    # Convert max_price to float if provided
    if max_price is not None:
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = None
    
    # Validate price range
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            return jsonify({"error": "Invalid price range: min_price cannot be greater than max_price"}), HTTP_BAD_REQUEST
    
    # Convert category_id to int if provided
    if category_id is not None:
        try:
            category_id = int(category_id)
        except ValueError:
            category_id = None
    
    result = get_shop_items(shop_id, search=search, category_id=category_id,
                           min_price=min_price, max_price=max_price,
                           availability=availability, sort=sort)
    if result is None:
        return jsonify({"error": "Shop not found"}), HTTP_NOT_FOUND
    return jsonify(result), HTTP_OK


@app.get("/items/<int:item_id>")
def get_item_details(item_id):
    """GET /items/<item_id> - Get item details"""
    item = get_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), HTTP_NOT_FOUND
    return jsonify(item), HTTP_OK


@app.get("/shops/<int:shop_id>/categories")
def list_shop_item_categories(shop_id):
    """GET /shops/<shop_id>/categories - Get item categories for a shop"""
    categories = get_shop_item_categories(shop_id)
    if categories is None:
        return jsonify({"error": "Shop not found"}), HTTP_NOT_FOUND
    return jsonify(categories), HTTP_OK