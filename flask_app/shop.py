"""
Shop API module - handles all shop-related endpoints.
Following TDD approach - minimal implementation to make tests pass.
"""
from flask import request, jsonify
from flask_app.app import app


def get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
    """Get shops with filtering and sorting"""
    return {
        "shops": [],
        "total": 0,
        "filters_applied": {}
    }


def get_shop_by_id(shop_id):
    """Get shop details by ID"""
    return None


def get_shop_hours(shop_id, start_date=None, end_date=None):
    """Get shop hours"""
    return None


def get_shop_categories():
    """Get all shop categories"""
    return {
        "categories": []
    }


def get_shop_catalog(shop_id, include_items=True):
    """Get shop catalog"""
    return None


def get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                   max_price=None, availability=None, sort=None):
    """Get shop items with filtering"""
    return None


def get_item_by_id(item_id):
    """Get item details by ID"""
    return None


def get_shop_item_categories(shop_id):
    """Get item categories for a shop"""
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
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    hours = get_shop_hours(shop_id, start_date=start_date, end_date=end_date)
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

