"""
Test suite for Shop API endpoints.
Following TDD approach - comprehensive test cases.
"""
import pytest
from datetime import datetime, time
from unittest.mock import Mock, patch


def test_get_shops_list_all(client, monkeypatch):
    """Test GET /shops - list all shops"""
    sample_shops = [
        {
            "id": 1,
            "name": "Tim Hortons",
            "category": "Food & Beverage",
            "description": "Coffee, donuts, and sandwiches",
            "terminal": "Terminal 1",
            "gate": "Gate A5",
            "location": "Domestic Terminal",
            "today_hours": {
                "open_time": "04:30",
                "close_time": "22:00",
                "is_open": True,
                "status": "Open now",
                "next_change": "22:00"
            }
        }
    ]
    
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        return {
            "shops": sample_shops,
            "total": 1,
            "filters_applied": {}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops")
    assert response.status_code == 200
    data = response.json
    assert "shops" in data
    assert "total" in data
    assert len(data["shops"]) == 1
    assert data["shops"][0]["id"] == 1
    assert data["shops"][0]["name"] == "Tim Hortons"


def test_get_shops_with_category_filter(client, monkeypatch):
    """Test GET /shops?category=Food%20%26%20Beverage"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert category == "Food & Beverage"
        return {
            "shops": [{"id": 1, "name": "Tim Hortons", "category": "Food & Beverage"}],
            "total": 1,
            "filters_applied": {"category": "Food & Beverage"}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?category=Food%20%26%20Beverage")
    assert response.status_code == 200
    data = response.json
    assert data["total"] == 1


def test_get_shops_with_open_now_filter_true(client, monkeypatch):
    """Test GET /shops?open_now=true"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert open_now is True
        return {
            "shops": [{"id": 1, "name": "Tim Hortons", "today_hours": {"is_open": True}}],
            "total": 1,
            "filters_applied": {"open_now": True}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?open_now=true")
    assert response.status_code == 200


def test_get_shops_with_open_now_filter_false(client, monkeypatch):
    """Test GET /shops?open_now=false"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert open_now is False
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"open_now": False}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?open_now=false")
    assert response.status_code == 200


def test_get_shops_with_sorting_name(client, monkeypatch):
    """Test GET /shops?sort=name"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert sort == "name"
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"sort": "name"}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?sort=name")
    assert response.status_code == 200


def test_get_shops_with_sorting_status(client, monkeypatch):
    """Test GET /shops?sort=status"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert sort == "status"
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"sort": "status"}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?sort=status")
    assert response.status_code == 200


def test_get_shops_with_sorting_gate(client, monkeypatch):
    """Test GET /shops?sort=gate"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert sort == "gate"
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"sort": "gate"}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?sort=gate")
    assert response.status_code == 200


def test_get_shops_with_terminal_filter(client, monkeypatch):
    """Test GET /shops?terminal=Terminal%201"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert terminal == "Terminal 1"
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"terminal": "Terminal 1"}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?terminal=Terminal%201")
    assert response.status_code == 200


def test_get_shops_with_gate_filter(client, monkeypatch):
    """Test GET /shops?gate=Gate%20A5"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert gate == "Gate A5"
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"gate": "Gate A5"}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?gate=Gate%20A5")
    assert response.status_code == 200


def test_get_shops_with_multiple_filters(client, monkeypatch):
    """Test GET /shops?category=Food&open_now=true&sort=name&terminal=Terminal%201"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert category == "Food"
        assert open_now is True
        assert sort == "name"
        assert terminal == "Terminal 1"
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"category": "Food", "open_now": True, "sort": "name", "terminal": "Terminal 1"}
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?category=Food&open_now=true&sort=name&terminal=Terminal%201")
    assert response.status_code == 200


def test_get_shop_by_id_success(client, monkeypatch):
    """Test GET /shops/<shop_id> - successful retrieval"""
    sample_shop = {
        "id": 1,
        "name": "Tim Hortons",
        "category": "Food & Beverage",
        "description": "Coffee, donuts, and sandwiches",
        "terminal": "Terminal 1",
        "gate": "Gate A5",
        "location": "Domestic Terminal",
        "today_hours": {
            "open_time": "04:30",
            "close_time": "22:00",
            "is_open": True,
            "status": "Open now",
            "next_change": "22:00"
        },
        "weekly_hours": [
            {
                "day": "Monday",
                "day_of_week": 1,
                "open_time": "04:30",
                "close_time": "22:00",
                "is_closed": False
            }
        ],
        "exception_hours": []
    }
    
    def fake_get_shop_by_id(shop_id):
        assert shop_id == 1
        return sample_shop
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_by_id", fake_get_shop_by_id)
    
    response = client.get("/shops/1")
    assert response.status_code == 200
    data = response.json
    assert data["id"] == 1
    assert data["name"] == "Tim Hortons"
    assert "weekly_hours" in data
    assert "exception_hours" in data
    assert data["today_hours"]["is_open"] is True


def test_get_shop_by_id_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id> - shop not found"""
    def fake_get_shop_by_id(shop_id):
        assert shop_id == 999
        return None
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_by_id", fake_get_shop_by_id)
    
    response = client.get("/shops/999")
    assert response.status_code == 404
    assert "error" in response.json
    assert "not found" in response.json["error"].lower()


def test_get_shop_by_id_invalid_id(client, monkeypatch):
    """Test GET /shops/<shop_id> - invalid ID format"""
    response = client.get("/shops/abc")
    assert response.status_code == 404  # Flask returns 404 for invalid int conversion


def test_get_shop_hours_success(client, monkeypatch):
    """Test GET /shops/<shop_id>/hours"""
    sample_hours = {
        "shop_id": 1,
        "shop_name": "Tim Hortons",
        "weekly_hours": [
            {
                "day": "Monday",
                "day_of_week": 1,
                "open_time": "04:30",
                "close_time": "22:00",
                "is_closed": False
            }
        ],
        "exception_hours": []
    }
    
    def fake_get_shop_hours(shop_id):
        assert shop_id == 1
        return sample_hours
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_hours", fake_get_shop_hours)
    
    response = client.get("/shops/1/hours")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "weekly_hours" in data
    assert "exception_hours" in data
    assert len(data["weekly_hours"]) == 1


def test_get_shop_hours_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/hours - shop not found"""
    def fake_get_shop_hours(shop_id):
        assert shop_id == 999
        return None
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_hours", fake_get_shop_hours)
    
    response = client.get("/shops/999/hours")
    assert response.status_code == 404
    assert "error" in response.json


def test_get_shop_categories(client, monkeypatch):
    """Test GET /shops/categories"""
    sample_categories = {
        "categories": [
            {"name": "Food & Beverage", "count": 15},
            {"name": "Retail", "count": 12},
            {"name": "Services", "count": 8}
        ]
    }
    
    def fake_get_shop_categories():
        return sample_categories
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_categories", fake_get_shop_categories)
    
    response = client.get("/shops/categories")
    assert response.status_code == 200
    data = response.json
    assert "categories" in data
    assert len(data["categories"]) == 3
    assert data["categories"][0]["name"] == "Food & Beverage"
    assert data["categories"][0]["count"] == 15


def test_get_shop_categories_empty(client, monkeypatch):
    """Test GET /shops/categories - empty result"""
    def fake_get_shop_categories():
        return {"categories": []}
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_categories", fake_get_shop_categories)
    
    response = client.get("/shops/categories")
    assert response.status_code == 200
    data = response.json
    assert data["categories"] == []


def test_get_shop_catalog_success(client, monkeypatch):
    """Test GET /shops/<shop_id>/catalog"""
    sample_catalog = {
        "shop_id": 1,
        "shop_name": "Tim Hortons",
        "categories": [
            {
                "category_id": 1,
                "category_name": "Beverages",
                "items": [
                    {
                        "item_id": 1,
                        "name": "Coffee",
                        "base_price": 2.49
                    }
                ]
            }
        ]
    }
    
    def fake_get_shop_catalog(shop_id, include_items=True):
        assert shop_id == 1
        assert include_items is True
        return sample_catalog
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_catalog", fake_get_shop_catalog)
    
    response = client.get("/shops/1/catalog?include_items=true")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "categories" in data
    assert len(data["categories"]) == 1


def test_get_shop_catalog_default_include_items(client, monkeypatch):
    """Test GET /shops/<shop_id>/catalog - default include_items=true"""
    def fake_get_shop_catalog(shop_id, include_items=True):
        assert shop_id == 1
        assert include_items is True
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "categories": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_catalog", fake_get_shop_catalog)
    
    response = client.get("/shops/1/catalog")
    assert response.status_code == 200


def test_get_shop_catalog_without_items(client, monkeypatch):
    """Test GET /shops/<shop_id>/catalog?include_items=false"""
    def fake_get_shop_catalog(shop_id, include_items=True):
        assert shop_id == 1
        assert include_items is False
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "categories": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_catalog", fake_get_shop_catalog)
    
    response = client.get("/shops/1/catalog?include_items=false")
    assert response.status_code == 200


def test_get_shop_catalog_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/catalog - shop not found"""
    def fake_get_shop_catalog(shop_id, include_items=True):
        assert shop_id == 999
        return None
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_catalog", fake_get_shop_catalog)
    
    response = client.get("/shops/999/catalog")
    assert response.status_code == 404
    assert "error" in response.json


def test_get_shop_items_success(client, monkeypatch):
    """Test GET /shops/<shop_id>/items"""
    sample_items = {
        "shop_id": 1,
        "shop_name": "Tim Hortons",
        "items": [
            {
                "item_id": 1,
                "name": "Coffee",
                "base_price": 2.49,
                "availability": "in_stock"
            }
        ]
    }
    
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        return sample_items
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "items" in data
    assert len(data["items"]) == 1


def test_get_shop_items_with_search(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?search=coffee"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert search == "coffee"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?search=coffee")
    assert response.status_code == 200


def test_get_shop_items_with_category_id(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?category_id=1"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert category_id == 1
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?category_id=1")
    assert response.status_code == 200


def test_get_shop_items_with_min_price(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?min_price=2.00"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert min_price == 2.00
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?min_price=2.00")
    assert response.status_code == 200


def test_get_shop_items_with_max_price(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?max_price=5.00"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert max_price == 5.00
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?max_price=5.00")
    assert response.status_code == 200


def test_get_shop_items_with_price_range(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?min_price=2.00&max_price=5.00"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert min_price == 2.00
        assert max_price == 5.00
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?min_price=2.00&max_price=5.00")
    assert response.status_code == 200


def test_get_shop_items_invalid_price_range(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?min_price=5.00&max_price=2.00 - should return 400"""
    response = client.get("/shops/1/items?min_price=5.00&max_price=2.00")
    assert response.status_code == 400
    assert "error" in response.json
    assert "price range" in response.json["error"].lower()


def test_get_shop_items_invalid_price_range_equal(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?min_price=5.00&max_price=5.00 - should be valid"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert min_price == 5.00
        assert max_price == 5.00
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?min_price=5.00&max_price=5.00")
    assert response.status_code == 200


def test_get_shop_items_with_availability_in_stock(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?availability=in_stock"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert availability == "in_stock"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?availability=in_stock")
    assert response.status_code == 200


def test_get_shop_items_with_availability_low_stock(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?availability=low_stock"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert availability == "low_stock"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?availability=low_stock")
    assert response.status_code == 200


def test_get_shop_items_with_availability_out_of_stock(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?availability=out_of_stock"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert availability == "out_of_stock"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?availability=out_of_stock")
    assert response.status_code == 200


def test_get_shop_items_with_sorting_name(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?sort=name"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert sort == "name"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?sort=name")
    assert response.status_code == 200


def test_get_shop_items_with_sorting_price_asc(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?sort=price_asc"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert sort == "price_asc"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?sort=price_asc")
    assert response.status_code == 200


def test_get_shop_items_with_sorting_price_desc(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?sort=price_desc"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert sort == "price_desc"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?sort=price_desc")
    assert response.status_code == 200


def test_get_shop_items_with_multiple_filters(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?search=coffee&category_id=1&min_price=2.00&max_price=5.00&availability=in_stock&sort=price_asc"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 1
        assert search == "coffee"
        assert category_id == 1
        assert min_price == 2.00
        assert max_price == 5.00
        assert availability == "in_stock"
        assert sort == "price_asc"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?search=coffee&category_id=1&min_price=2.00&max_price=5.00&availability=in_stock&sort=price_asc")
    assert response.status_code == 200


def test_get_shop_items_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/items - shop not found"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None):
        assert shop_id == 999
        return None
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/999/items")
    assert response.status_code == 404
    assert "error" in response.json


def test_get_item_by_id_success(client, monkeypatch):
    """Test GET /items/<item_id>"""
    sample_item = {
        "item_id": 1,
        "name": "Coffee",
        "base_price": 2.49,
        "description": "Fresh brewed coffee",
        "variants": [
            {
                "variant_type": "Size",
                "variant_value": "Small",
                "price_adjustment": 0.00,
                "final_price": 2.49
            },
            {
                "variant_type": "Size",
                "variant_value": "Large",
                "price_adjustment": 1.00,
                "final_price": 3.49
            }
        ],
        "variant_types": ["Size"]
    }
    
    def fake_get_item_by_id(item_id):
        assert item_id == 1
        return sample_item
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_item_by_id", fake_get_item_by_id)
    
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json
    assert data["item_id"] == 1
    assert data["name"] == "Coffee"
    assert "variants" in data
    assert "variant_types" in data
    assert len(data["variants"]) == 2


def test_get_item_by_id_not_found(client, monkeypatch):
    """Test GET /items/<item_id> - item not found"""
    def fake_get_item_by_id(item_id):
        assert item_id == 999
        return None
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_item_by_id", fake_get_item_by_id)
    
    response = client.get("/items/999")
    assert response.status_code == 404
    assert "error" in response.json


def test_get_item_by_id_invalid_id(client, monkeypatch):
    """Test GET /items/<item_id> - invalid ID format"""
    response = client.get("/items/abc")
    assert response.status_code == 404  # Flask returns 404 for invalid int conversion


def test_get_shop_item_categories(client, monkeypatch):
    """Test GET /shops/<shop_id>/categories"""
    sample_categories = {
        "shop_id": 1,
        "shop_name": "Tim Hortons",
        "categories": [
            {"category_id": 1, "category_name": "Beverages", "item_count": 10},
            {"category_id": 2, "category_name": "Food", "item_count": 5},
            {"category_id": 3, "category_name": "Desserts", "item_count": 8}
        ]
    }
    
    def fake_get_shop_item_categories(shop_id):
        assert shop_id == 1
        return sample_categories
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_item_categories", fake_get_shop_item_categories)
    
    response = client.get("/shops/1/categories")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "categories" in data
    assert len(data["categories"]) == 3
    assert data["categories"][0]["category_name"] == "Beverages"


def test_get_shop_item_categories_empty(client, monkeypatch):
    """Test GET /shops/<shop_id>/categories - empty categories"""
    def fake_get_shop_item_categories(shop_id):
        assert shop_id == 1
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "categories": []
        }
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_item_categories", fake_get_shop_item_categories)
    
    response = client.get("/shops/1/categories")
    assert response.status_code == 200
    data = response.json
    assert data["categories"] == []


def test_get_shop_item_categories_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/categories - shop not found"""
    def fake_get_shop_item_categories(shop_id):
        assert shop_id == 999
        return None
    
    import flask_app.shop as shop
    monkeypatch.setattr(shop, "get_shop_item_categories", fake_get_shop_item_categories)
    
    response = client.get("/shops/999/categories")
    assert response.status_code == 404
    assert "error" in response.json
