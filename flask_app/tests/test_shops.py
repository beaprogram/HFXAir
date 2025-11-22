"""
Test suite for Shop API endpoints.
Following TDD approach - these tests should fail initially.
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
    
    def fake_get_shops():
        return {
            "shops": sample_shops,
            "total": 1,
            "filters_applied": {}
        }
    
    import shop
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
    
    import shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?category=Food%20%26%20Beverage")
    assert response.status_code == 200
    data = response.json
    assert data["total"] == 1


def test_get_shops_with_open_now_filter(client, monkeypatch):
    """Test GET /shops?open_now=true"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert open_now is True
        return {
            "shops": [{"id": 1, "name": "Tim Hortons", "today_hours": {"is_open": True}}],
            "total": 1,
            "filters_applied": {"open_now": True}
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?open_now=true")
    assert response.status_code == 200


def test_get_shops_with_sorting(client, monkeypatch):
    """Test GET /shops?sort=status"""
    def fake_get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
        assert sort == "status"
        return {
            "shops": [],
            "total": 0,
            "filters_applied": {"sort": "status"}
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?sort=status")
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
    
    import shop
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
    
    import shop
    monkeypatch.setattr(shop, "get_shops", fake_get_shops)
    
    response = client.get("/shops?gate=Gate%20A5")
    assert response.status_code == 200


def test_get_shop_by_id_success(client, monkeypatch):
    """Test GET /shops/<shop_id> - successful retrieval"""
    sample_shop = {
        "id": 1,
        "name": "Tim Hortons",
        "category": "Food & Beverage",
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
    
    import shop
    monkeypatch.setattr(shop, "get_shop_by_id", fake_get_shop_by_id)
    
    response = client.get("/shops/1")
    assert response.status_code == 200
    data = response.json
    assert data["id"] == 1
    assert data["name"] == "Tim Hortons"
    assert "weekly_hours" in data
    assert "exception_hours" in data


def test_get_shop_by_id_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id> - shop not found"""
    def fake_get_shop_by_id(shop_id):
        assert shop_id == 999
        return None
    
    import shop
    monkeypatch.setattr(shop, "get_shop_by_id", fake_get_shop_by_id)
    
    response = client.get("/shops/999")
    assert response.status_code == 404
    assert "error" in response.json
    assert "not found" in response.json["error"].lower()


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
    
    def fake_get_shop_hours(shop_id, start_date=None, end_date=None):
        assert shop_id == 1
        return sample_hours
    
    import shop
    monkeypatch.setattr(shop, "get_shop_hours", fake_get_shop_hours)
    
    response = client.get("/shops/1/hours")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "weekly_hours" in data
    assert "exception_hours" in data


def test_get_shop_hours_with_date_range(client, monkeypatch):
    """Test GET /shops/<shop_id>/hours?start_date=2024-12-01&end_date=2024-12-31"""
    def fake_get_shop_hours(shop_id, start_date=None, end_date=None):
        assert shop_id == 1
        assert start_date == "2024-12-01"
        assert end_date == "2024-12-31"
        return {
            "shop_id": 1,
            "weekly_hours": [],
            "exception_hours": []
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shop_hours", fake_get_shop_hours)
    
    response = client.get("/shops/1/hours?start_date=2024-12-01&end_date=2024-12-31")
    assert response.status_code == 200


def test_get_shop_hours_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/hours - shop not found"""
    def fake_get_shop_hours(shop_id, start_date=None, end_date=None):
        assert shop_id == 999
        return None
    
    import shop
    monkeypatch.setattr(shop, "get_shop_hours", fake_get_shop_hours)
    
    response = client.get("/shops/999/hours")
    assert response.status_code == 404


def test_get_shop_categories(client, monkeypatch):
    """Test GET /shops/categories"""
    sample_categories = {
        "categories": [
            {"name": "Food & Beverage", "count": 15},
            {"name": "Retail", "count": 12}
        ]
    }
    
    def fake_get_shop_categories():
        return sample_categories
    
    import shop
    monkeypatch.setattr(shop, "get_shop_categories", fake_get_shop_categories)
    
    response = client.get("/shops/categories")
    assert response.status_code == 200
    data = response.json
    assert "categories" in data
    assert len(data["categories"]) == 2
    assert data["categories"][0]["name"] == "Food & Beverage"
    assert data["categories"][0]["count"] == 15


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
    
    import shop
    monkeypatch.setattr(shop, "get_shop_catalog", fake_get_shop_catalog)
    
    response = client.get("/shops/1/catalog?include_items=true")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "categories" in data


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
    
    import shop
    monkeypatch.setattr(shop, "get_shop_catalog", fake_get_shop_catalog)
    
    response = client.get("/shops/1/catalog?include_items=false")
    assert response.status_code == 200


def test_get_shop_catalog_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/catalog - shop not found"""
    def fake_get_shop_catalog(shop_id, include_items=True):
        assert shop_id == 999
        return None
    
    import shop
    monkeypatch.setattr(shop, "get_shop_catalog", fake_get_shop_catalog)
    
    response = client.get("/shops/999/catalog")
    assert response.status_code == 404


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
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total_items": 1,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False
        }
    }
    
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None, page=1, per_page=20):
        assert shop_id == 1
        return sample_items
    
    import shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "items" in data
    assert "pagination" in data


def test_get_shop_items_with_search(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?search=coffee"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None, page=1, per_page=20):
        assert shop_id == 1
        assert search == "coffee"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": [],
            "pagination": {"page": 1, "per_page": 20, "total_items": 0, "total_pages": 0, "has_next": False, "has_prev": False}
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?search=coffee")
    assert response.status_code == 200


def test_get_shop_items_with_price_range(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?min_price=2.00&max_price=5.00"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None, page=1, per_page=20):
        assert shop_id == 1
        assert min_price == 2.00
        assert max_price == 5.00
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": [],
            "pagination": {"page": 1, "per_page": 20, "total_items": 0, "total_pages": 0, "has_next": False, "has_prev": False}
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?min_price=2.00&max_price=5.00")
    assert response.status_code == 200


def test_get_shop_items_invalid_price_range(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?min_price=5.00&max_price=2.00 - should return 400"""
    response = client.get("/shops/1/items?min_price=5.00&max_price=2.00")
    assert response.status_code == 400
    assert "error" in response.json
    assert "price range" in response.json["error"].lower()


def test_get_shop_items_with_availability(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?availability=in_stock"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None, page=1, per_page=20):
        assert shop_id == 1
        assert availability == "in_stock"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": [],
            "pagination": {"page": 1, "per_page": 20, "total_items": 0, "total_pages": 0, "has_next": False, "has_prev": False}
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?availability=in_stock")
    assert response.status_code == 200


def test_get_shop_items_with_sorting(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?sort=price_asc"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None, page=1, per_page=20):
        assert shop_id == 1
        assert sort == "price_asc"
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": [],
            "pagination": {"page": 1, "per_page": 20, "total_items": 0, "total_pages": 0, "has_next": False, "has_prev": False}
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?sort=price_asc")
    assert response.status_code == 200


def test_get_shop_items_with_pagination(client, monkeypatch):
    """Test GET /shops/<shop_id>/items?page=2&per_page=10"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None, page=1, per_page=20):
        assert shop_id == 1
        assert page == 2
        assert per_page == 10
        return {
            "shop_id": 1,
            "shop_name": "Tim Hortons",
            "items": [],
            "pagination": {"page": 2, "per_page": 10, "total_items": 0, "total_pages": 0, "has_next": False, "has_prev": True}
        }
    
    import shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/1/items?page=2&per_page=10")
    assert response.status_code == 200


def test_get_shop_items_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/items - shop not found"""
    def fake_get_shop_items(shop_id, search=None, category_id=None, min_price=None, 
                           max_price=None, availability=None, sort=None, page=1, per_page=20):
        assert shop_id == 999
        return None
    
    import shop
    monkeypatch.setattr(shop, "get_shop_items", fake_get_shop_items)
    
    response = client.get("/shops/999/items")
    assert response.status_code == 404


def test_get_item_by_id_success(client, monkeypatch):
    """Test GET /items/<item_id>"""
    sample_item = {
        "item_id": 1,
        "name": "Coffee",
        "base_price": 2.49,
        "variants": [
            {
                "variant_type": "Size",
                "variant_value": "Small",
                "price_adjustment": 0.00,
                "final_price": 2.49
            }
        ],
        "variant_types": ["Size"]
    }
    
    def fake_get_item_by_id(item_id):
        assert item_id == 1
        return sample_item
    
    import shop
    monkeypatch.setattr(shop, "get_item_by_id", fake_get_item_by_id)
    
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json
    assert data["item_id"] == 1
    assert data["name"] == "Coffee"
    assert "variants" in data
    assert "variant_types" in data


def test_get_item_by_id_not_found(client, monkeypatch):
    """Test GET /items/<item_id> - item not found"""
    def fake_get_item_by_id(item_id):
        assert item_id == 999
        return None
    
    import shop
    monkeypatch.setattr(shop, "get_item_by_id", fake_get_item_by_id)
    
    response = client.get("/items/999")
    assert response.status_code == 404
    assert "error" in response.json


def test_get_shop_item_categories(client, monkeypatch):
    """Test GET /shops/<shop_id>/categories"""
    sample_categories = {
        "shop_id": 1,
        "shop_name": "Tim Hortons",
        "categories": [
            {"category_id": 1, "category_name": "Beverages", "item_count": 10},
            {"category_id": 2, "category_name": "Food", "item_count": 5}
        ]
    }
    
    def fake_get_shop_item_categories(shop_id):
        assert shop_id == 1
        return sample_categories
    
    import shop
    monkeypatch.setattr(shop, "get_shop_item_categories", fake_get_shop_item_categories)
    
    response = client.get("/shops/1/categories")
    assert response.status_code == 200
    data = response.json
    assert data["shop_id"] == 1
    assert "categories" in data
    assert len(data["categories"]) == 2


def test_get_shop_item_categories_not_found(client, monkeypatch):
    """Test GET /shops/<shop_id>/categories - shop not found"""
    def fake_get_shop_item_categories(shop_id):
        assert shop_id == 999
        return None
    
    import shop
    monkeypatch.setattr(shop, "get_shop_item_categories", fake_get_shop_item_categories)
    
    response = client.get("/shops/999/categories")
    assert response.status_code == 404

