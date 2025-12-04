"""
Shop API module - handles all shop-related endpoints.
Following TDD approach - minimal implementation to make tests pass.
"""
from flask import request, jsonify
from flask_app.app import app, get_db_connection
from datetime import datetime, time, timedelta
import logging
import pytz

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
                        open_time = datetime.strptime(str(open_t)[:5], "%H:%M").time()
                    
                    if isinstance(close_t, time):
                        close_time = close_t
                    else:
                        close_time = datetime.strptime(str(close_t)[:5], "%H:%M").time()
                    
                    is_open = open_time <= current_time <= close_time
                    
                    if is_open:
                        status = "Open now"
                        next_change = close_time.strftime("%H:%M")
                    elif current_time < open_time:
                        status = f"Opens at {open_time.strftime('%H:%M')}"
                        next_change = open_time.strftime("%H:%M")
                    else:
                        status = f"Opens at {open_time.strftime('%H:%M')}"
                        next_change = open_time.strftime("%H:%M")
                except Exception:
                    status = "Unknown"
            elif is_closed:
                status = "Closed today"
            
            # Apply open_now filter if specified
            if open_now is not None:
                if open_now and not is_open:
                    continue
                if not open_now and is_open:
                    continue
            
            today_hours = {
                "open_time": open_t.strftime("%H:%M") if open_t and isinstance(open_t, time) else (str(open_t)[:5] if open_t else None),
                "close_time": close_t.strftime("%H:%M") if close_t and isinstance(close_t, time) else (str(close_t)[:5] if close_t else None),
                "is_open": is_open,
                "status": status,
                "next_change": next_change
            }
            
            shops.append({
                "id": shop_id,
                "name": name,
                "category": cat,
                "description": desc,
                "terminal": term,
                "gate": gate_val,
                "location": loc,
                "today_hours": today_hours
            })
        
        # Apply status sorting if requested
        if sort == "status":
            shops.sort(key=lambda x: (not x["today_hours"]["is_open"], x["name"]))
        
        if category:
            filters_applied["category"] = category
        if open_now is not None:
            filters_applied["open_now"] = open_now
        if sort:
            filters_applied["sort"] = sort
        if terminal:
            filters_applied["terminal"] = terminal
        if gate:
            filters_applied["gate"] = gate
        
        cur.close()
        conn.close()
        
        return {
            "shops": shops,
            "total": len(shops),
            "filters_applied": filters_applied
        }
    except Exception as e:
        logging.error(f"Error fetching shops: {e}")
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {}
        }


def get_shop_by_id(shop_id):
    """Get shop details by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get shop basic info
        query = """
            SELECT shop_id, name, category, description, terminal, gate, location_description
            FROM shops
            WHERE shop_id = %s
        """
        cur.execute(query, (shop_id,))
        row = cur.fetchone()
        
        if not row:
            cur.close()
            conn.close()
            return None
        
        shop_id_db, name, category, description, terminal, gate, location_description = row
        
        # Get today's hours
        current_day = datetime.now(HALIFAX_TZ).weekday()
        current_time = datetime.now(HALIFAX_TZ).time()
        
        hours_query = """
            SELECT open_time, close_time, is_closed
            FROM shop_hours
            WHERE shop_id = %s AND day_of_week = %s
        """
        cur.execute(hours_query, (shop_id, current_day))
        hours_row = cur.fetchone()
        
        today_hours = {
            "open_time": None,
            "close_time": None,
            "is_open": False,
            "status": "Unknown",
            "next_change": None
        }
        
        if hours_row:
            open_t, close_t, is_closed = hours_row
            if not is_closed and open_t and close_t:
                # Convert timedelta or time objects to time objects for comparison
                try:
                    if isinstance(open_t, time):
                        open_time = open_t
                    elif isinstance(open_t, timedelta):
                        # Convert timedelta to time object
                        total_seconds = int(open_t.total_seconds())
                        hours = (total_seconds // 3600) % 24
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        open_time = time(hours, minutes, seconds)
                    else:
                        open_time = datetime.strptime(str(open_t)[:5], "%H:%M").time()
                    
                    if isinstance(close_t, time):
                        close_time = close_t
                    elif isinstance(close_t, timedelta):
                        # Convert timedelta to time object
                        total_seconds = int(close_t.total_seconds())
                        hours = (total_seconds // 3600) % 24
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        close_time = time(hours, minutes, seconds)
                    else:
                        close_time = datetime.strptime(str(close_t)[:5], "%H:%M").time()
                    
                    is_open = open_time <= current_time <= close_time
                except (ValueError, AttributeError) as e:
                    logging.warning(f"Error converting time values for shop {shop_id}: {e}")
                    is_open = False
                    open_time = open_t
                    close_time = close_t
                
                today_hours = {
                    "open_time": open_time.strftime("%H:%M") if isinstance(open_time, time) else str(open_time)[:5],
                    "close_time": close_time.strftime("%H:%M") if isinstance(close_time, time) else str(close_time)[:5],
                    "is_open": is_open,
                    "status": "Open now" if is_open else f"Opens at {open_time.strftime('%H:%M') if isinstance(open_time, time) else str(open_time)[:5]}",
                    "next_change": (close_time.strftime("%H:%M") if isinstance(close_time, time) else str(close_time)[:5]) if is_open else (open_time.strftime("%H:%M") if isinstance(open_time, time) else str(open_time)[:5])
                }
            elif is_closed:
                today_hours["status"] = "Closed today"
        
        # Get weekly hours
        weekly_query = """
            SELECT day_of_week, open_time, close_time, is_closed
            FROM shop_hours
            WHERE shop_id = %s
            ORDER BY day_of_week
        """
        cur.execute(weekly_query, (shop_id,))
        weekly_rows = cur.fetchall()
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_hours = []
        
        for day_num, open_t, close_t, is_closed in weekly_rows:
            weekly_hours.append({
                "day": days[day_num],
                "day_of_week": day_num,
                "open_time": open_t.strftime("%H:%M") if open_t and isinstance(open_t, time) else (str(open_t)[:5] if open_t else None),
                "close_time": close_t.strftime("%H:%M") if close_t and isinstance(close_t, time) else (str(close_t)[:5] if close_t else None),
                "is_closed": bool(is_closed) if is_closed is not None else False
            })
        
        # Get exception hours
        exception_query = """
            SELECT exception_date, open_time, close_time, is_closed, reason
            FROM shop_hour_exceptions
            WHERE shop_id = %s
            ORDER BY exception_date DESC
            LIMIT 10
        """
        cur.execute(exception_query, (shop_id,))
        exception_rows = cur.fetchall()
        
        exception_hours = []
        for exc_date, open_t, close_t, is_closed, desc in exception_rows:
            exception_hours.append({
                "date": exc_date.strftime("%Y-%m-%d") if exc_date else None,
                "open_time": open_t.strftime("%H:%M") if open_t and isinstance(open_t, time) else (str(open_t)[:5] if open_t else None),
                "close_time": close_t.strftime("%H:%M") if close_t and isinstance(close_t, time) else (str(close_t)[:5] if close_t else None),
                "is_closed": bool(is_closed) if is_closed is not None else False,
                "description": desc
            })
        
        cur.close()
        conn.close()
        
        return {
            "id": shop_id_db,
            "name": name,
            "category": category,
            "description": description,
            "terminal": terminal,
            "gate": gate,
            "location": location_description,
            "today_hours": today_hours,
            "weekly_hours": weekly_hours,
            "exception_hours": exception_hours
        }
    except Exception as e:
        import traceback
        logging.error(f"Error fetching shop by ID {shop_id}: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return None


def get_shop_hours(shop_id):
    """Get shop hours"""
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
        
        # Get weekly hours
        weekly_query = """
            SELECT day_of_week, open_time, close_time, is_closed
            FROM shop_hours
            WHERE shop_id = %s
            ORDER BY day_of_week
        """
        cur.execute(weekly_query, (shop_id,))
        weekly_rows = cur.fetchall()
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_hours = []
        
        for day_num, open_t, close_t, is_closed in weekly_rows:
            weekly_hours.append({
                "day": days[day_num],
                "day_of_week": day_num,
                "open_time": open_t.strftime("%H:%M") if open_t and isinstance(open_t, time) else (str(open_t)[:5] if open_t else None),
                "close_time": close_t.strftime("%H:%M") if close_t and isinstance(close_t, time) else (str(close_t)[:5] if close_t else None),
                "is_closed": bool(is_closed) if is_closed is not None else False
            })
        
        # Get exception hours
        exception_query = """
            SELECT exception_date, open_time, close_time, is_closed, reason
            FROM shop_hour_exceptions
            WHERE shop_id = %s
            ORDER BY exception_date DESC
        """
        
        cur.execute(exception_query, (shop_id,))
        exception_rows = cur.fetchall()
        
        exception_hours = []
        for exc_date, open_t, close_t, is_closed, desc in exception_rows:
            exception_hours.append({
                "date": exc_date.strftime("%Y-%m-%d") if exc_date else None,
                "open_time": open_t.strftime("%H:%M") if open_t and isinstance(open_t, time) else (str(open_t)[:5] if open_t else None),
                "close_time": close_t.strftime("%H:%M") if close_t and isinstance(close_t, time) else (str(close_t)[:5] if close_t else None),
                "is_closed": bool(is_closed) if is_closed is not None else False,
                "description": desc
            })
        
        cur.close()
        conn.close()
        
        return {
            "shop_id": shop_id_db,
            "shop_name": shop_name,
            "weekly_hours": weekly_hours,
            "exception_hours": exception_hours
        }
    except Exception as e:
        logging.error(f"Error fetching shop hours: {e}")
        return None


def get_shop_categories():
    """Get all shop categories"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT category, COUNT(*) as count
            FROM shops
            GROUP BY category
            ORDER BY category
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        categories = []
        for cat, count in rows:
            categories.append({
                "name": cat,
                "count": count
            })
        
        cur.close()
        conn.close()
        
        return {
            "categories": categories
        }
    except Exception as e:
        logging.error(f"Error fetching shop categories: {e}")
        return {
            "categories": []
        }


def get_shop_catalog(shop_id, include_items=True):
    """Get shop catalog"""
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
        
        # Get categories
        categories_query = """
            SELECT DISTINCT ic.category_id, ic.category_name
            FROM item_categories ic
            INNER JOIN items i ON ic.category_id = i.category_id
            WHERE i.shop_id = %s
            ORDER BY ic.category_name
        """
        cur.execute(categories_query, (shop_id,))
        category_rows = cur.fetchall()
        
        categories = []
        for cat_id, cat_name in category_rows:
            category_data = {
                "category_id": cat_id,
                "category_name": cat_name
            }
            
            if include_items:
                # Get items for this category
                items_query = """
                    SELECT item_id, name, base_price, description
                    FROM items
                    WHERE shop_id = %s AND category_id = %s
                    ORDER BY name
                """
                cur.execute(items_query, (shop_id, cat_id))
                item_rows = cur.fetchall()
                
                items = []
                for item_id, name, price, desc in item_rows:
                    items.append({
                        "item_id": item_id,
                        "name": name,
                        "base_price": float(price) if price else 0.0,
                        "description": desc
                    })
                
                category_data["items"] = items
            
            categories.append(category_data)
        
        cur.close()
        conn.close()
        
        return {
            "shop_id": shop_id_db,
            "shop_name": shop_name,
            "categories": categories
        }
    except Exception as e:
        logging.error(f"Error fetching shop catalog: {e}")
        return None


def get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                   max_price=None, availability=None, sort=None):
    """Get shop items with filtering"""
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
        
        # Build WHERE clause
        where_conditions = ["i.shop_id = %s"]
        params = [shop_id]
        
        if search:
            where_conditions.append("(i.name LIKE %s OR i.description LIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
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
            if availability == "in_stock":
                where_conditions.append("i.availability = 'in_stock'")
            elif availability == "low_stock":
                where_conditions.append("i.availability = 'low_stock'")
            elif availability == "out_of_stock":
                where_conditions.append("i.availability = 'out_of_stock'")
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Build ORDER BY clause
        order_by = "ORDER BY i.name"
        if sort == "name":
            order_by = "ORDER BY i.name"
        elif sort == "price_asc":
            order_by = "ORDER BY i.base_price ASC"
        elif sort == "price_desc":
            order_by = "ORDER BY i.base_price DESC"
        
        query = f"""
            SELECT item_id, name, base_price, description, availability, stock_quantity, image_url
            FROM items i
            {where_clause}
            {order_by}
        """
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        items = []
        for item_id, name, price, desc, avail, stock_qty, image_url in rows:
            # Get variants for this item
            variants_query = """
                SELECT variant_type, variant_value, price_adjustment
                FROM item_variants
                WHERE item_id = %s
                ORDER BY variant_type, variant_value
            """
            cur.execute(variants_query, (item_id,))
            variant_rows = cur.fetchall()
            
            variants = []
            variant_types_set = set()
            for var_type, var_value, price_adj in variant_rows:
                variant_types_set.add(var_type)
                variants.append({
                    "variant_type": var_type,
                    "variant_value": var_value,
                    "price_adjustment": float(price_adj) if price_adj else 0.0,
                    "final_price": float(price) + (float(price_adj) if price_adj else 0.0)
                })
            
            items.append({
                "item_id": item_id,
                "name": name,
                "base_price": float(price) if price else 0.0,
                "description": desc,
                "availability": avail,
                "stock_quantity": stock_qty,
                "image_url": image_url, 
                "variants": variants,
                "variant_types": list(variant_types_set)
            })
        
        cur.close()
        conn.close()
        
        return {
            "shop_id": shop_id_db,
            "shop_name": shop_name,
            "items": items
        }
    except Exception as e:
        logging.error(f"Error fetching shop items: {e}")
        return None


def get_item_by_id(item_id):
    """Get item details by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get item basic info
        query = """
            SELECT item_id, name, base_price, description
            FROM items
            WHERE item_id = %s
        """
        cur.execute(query, (item_id,))
        row = cur.fetchone()
        
        if not row:
            cur.close()
            conn.close()
            return None
        
        item_id_db, name, base_price, description = row
        
        # Get variants
        variants_query = """
            SELECT variant_type, variant_value, price_adjustment
            FROM item_variants
            WHERE item_id = %s
            ORDER BY variant_type, variant_value
        """
        cur.execute(variants_query, (item_id,))
        variant_rows = cur.fetchall()
        
        variants = []
        variant_types_set = set()
        
        for var_type, var_value, price_adj in variant_rows:
            variant_types_set.add(var_type)
            final_price = float(base_price) + (float(price_adj) if price_adj else 0.0)
            variants.append({
                "variant_type": var_type,
                "variant_value": var_value,
                "price_adjustment": float(price_adj) if price_adj else 0.0,
                "final_price": final_price
            })
        
        # If no variants, create a default one
        if not variants:
            variants.append({
                "variant_type": "Default",
                "variant_value": "Standard",
                "price_adjustment": 0.00,
                "final_price": float(base_price) if base_price else 0.0
            })
            variant_types_set.add("Default")
        
        cur.close()
        conn.close()
        
        return {
            "item_id": item_id_db,
            "name": name,
            "base_price": float(base_price) if base_price else 0.0,
            "description": description,
            "variants": variants,
            "variant_types": list(variant_types_set)
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
    return jsonify(result), 200


@app.get("/shops/<int:shop_id>")
def get_shop_details(shop_id):
    """GET /shops/<shop_id> - Get shop details"""
    shop = get_shop_by_id(shop_id)
    if shop is None:
        return jsonify({"error": "Shop not found"}), 404
    return jsonify(shop), 200


@app.get("/shops/<int:shop_id>/hours")
def get_shop_hours_route(shop_id):
    """GET /shops/<shop_id>/hours - Get shop hours"""
    hours = get_shop_hours(shop_id)
    if hours is None:
        return jsonify({"error": "Shop not found"}), 404
    return jsonify(hours), 200


@app.get("/shops/categories")
def list_shop_categories():
    """GET /shops/categories - Get all shop categories"""
    result = get_shop_categories()
    return jsonify(result), 200


@app.get("/shops/<int:shop_id>/catalog")
def get_shop_catalog_route(shop_id):
    """GET /shops/<shop_id>/catalog - Get shop catalog"""
    include_items = request.args.get("include_items", "true")
    include_items = include_items.lower() == "true"
    
    catalog = get_shop_catalog(shop_id, include_items=include_items)
    if catalog is None:
        return jsonify({"error": "Shop not found"}), 404
    return jsonify(catalog), 200


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
            return jsonify({"error": "Invalid price range: min_price cannot be greater than max_price"}), 400
    
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
        return jsonify({"error": "Shop not found"}), 404
    return jsonify(result), 200


@app.get("/items/<int:item_id>")
def get_item_details(item_id):
    """GET /items/<item_id> - Get item details"""
    item = get_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.get("/shops/<int:shop_id>/categories")
def list_shop_item_categories(shop_id):
    """GET /shops/<shop_id>/categories - Get item categories for a shop"""
    categories = get_shop_item_categories(shop_id)
    if categories is None:
        return jsonify({"error": "Shop not found"}), 404
    return jsonify(categories), 200
