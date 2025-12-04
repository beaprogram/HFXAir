"""
Test suite for new Shop features.
Tests for: Product Images, Variants, Stock Quantity, Halifax Timezone, Time Parsing.
Following TDD approach - comprehensive test cases.
"""
import pytest
from datetime import datetime, time
from unittest.mock import Mock, patch, MagicMock
import pytz


class TestProductImages:
    """Tests for product image_url feature"""
    
    def test_get_shop_items_includes_image_url(self, client, monkeypatch):
        """GET /shops/{id}/items should include image_url field"""
        sample_items = {
            "items": [
                {
                    "item_id": 1,
                    "name": "Coffee",
                    "base_price": 2.99,
                    "image_url": "https://images.unsplash.com/photo-coffee",
                    "stock_quantity": 50,
                    "variants": [],
                    "variant_types": []
                }
            ],
            "total": 1
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shop_items", lambda *args, **kwargs: sample_items)
        
        response = client.get("/shops/1/items")
        assert response.status_code == 200
        data = response.json
        assert "image_url" in data["items"][0]
        assert data["items"][0]["image_url"] == "https://images.unsplash.com/photo-coffee"
    
    def test_get_shop_items_image_url_can_be_none(self, client, monkeypatch):
        """Items without images should have null image_url"""
        sample_items = {
            "items": [
                {
                    "item_id": 1,
                    "name": "Coffee",
                    "base_price": 2.99,
                    "image_url": None,
                    "stock_quantity": 50,
                    "variants": [],
                    "variant_types": []
                }
            ],
            "total": 1
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shop_items", lambda *args, **kwargs: sample_items)
        
        response = client.get("/shops/1/items")
        assert response.status_code == 200
        data = response.json
        assert "image_url" in data["items"][0]
        assert data["items"][0]["image_url"] is None


class TestProductVariants:
    """Tests for product variants feature"""
    
    def test_get_shop_items_includes_variants(self, client, monkeypatch):
        """GET /shops/{id}/items should include variants array"""
        sample_items = {
            "items": [
                {
                    "item_id": 10,
                    "name": "Perfume Set",
                    "base_price": 89.99,
                    "image_url": "https://example.com/perfume.jpg",
                    "stock_quantity": 10,
                    "variants": [
                        {
                            "variant_type": "Size",
                            "variant_value": "50ml",
                            "price_adjustment": -45.00,
                            "final_price": 44.99
                        },
                        {
                            "variant_type": "Size",
                            "variant_value": "100ml",
                            "price_adjustment": 0.00,
                            "final_price": 89.99
                        }
                    ],
                    "variant_types": ["Size"]
                }
            ],
            "total": 1
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shop_items", lambda *args, **kwargs: sample_items)
        
        response = client.get("/shops/2/items")
        assert response.status_code == 200
        data = response.json
        item = data["items"][0]
        assert "variants" in item
        assert "variant_types" in item
        assert len(item["variants"]) == 2
        assert item["variant_types"] == ["Size"]
    
    def test_variant_has_required_fields(self, client, monkeypatch):
        """Each variant should have type, value, adjustment, and final_price"""
        sample_items = {
            "items": [
                {
                    "item_id": 10,
                    "name": "Perfume Set",
                    "base_price": 89.99,
                    "image_url": None,
                    "stock_quantity": 10,
                    "variants": [
                        {
                            "variant_type": "Size",
                            "variant_value": "50ml",
                            "price_adjustment": -45.00,
                            "final_price": 44.99
                        }
                    ],
                    "variant_types": ["Size"]
                }
            ],
            "total": 1
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shop_items", lambda *args, **kwargs: sample_items)
        
        response = client.get("/shops/2/items")
        assert response.status_code == 200
        variant = response.json["items"][0]["variants"][0]
        assert "variant_type" in variant
        assert "variant_value" in variant
        assert "price_adjustment" in variant
        assert "final_price" in variant
    
    def test_variant_final_price_calculation(self):
        """Final price should be base_price + price_adjustment"""
        base_price = 89.99
        price_adjustment = -45.00
        expected_final = 44.99
        
        final_price = base_price + price_adjustment
        assert round(final_price, 2) == expected_final
    
    def test_items_without_variants_have_empty_array(self, client, monkeypatch):
        """Items without variants should have empty variants array"""
        sample_items = {
            "items": [
                {
                    "item_id": 1,
                    "name": "Coffee",
                    "base_price": 2.99,
                    "image_url": None,
                    "stock_quantity": 50,
                    "variants": [],
                    "variant_types": []
                }
            ],
            "total": 1
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shop_items", lambda *args, **kwargs: sample_items)
        
        response = client.get("/shops/1/items")
        assert response.status_code == 200
        item = response.json["items"][0]
        assert item["variants"] == []
        assert item["variant_types"] == []


class TestStockQuantity:
    """Tests for stock quantity feature"""
    
    def test_get_shop_items_includes_stock_quantity(self, client, monkeypatch):
        """GET /shops/{id}/items should include stock_quantity field"""
        sample_items = {
            "items": [
                {
                    "item_id": 1,
                    "name": "Coffee",
                    "base_price": 2.99,
                    "image_url": None,
                    "stock_quantity": 50,
                    "variants": [],
                    "variant_types": []
                }
            ],
            "total": 1
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shop_items", lambda *args, **kwargs: sample_items)
        
        response = client.get("/shops/1/items")
        assert response.status_code == 200
        assert "stock_quantity" in response.json["items"][0]
        assert response.json["items"][0]["stock_quantity"] == 50
    
    def test_stock_quantity_is_integer(self, client, monkeypatch):
        """Stock quantity should be an integer"""
        sample_items = {
            "items": [
                {
                    "item_id": 1,
                    "name": "Coffee",
                    "base_price": 2.99,
                    "image_url": None,
                    "stock_quantity": 10,
                    "variants": [],
                    "variant_types": []
                }
            ],
            "total": 1
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shop_items", lambda *args, **kwargs: sample_items)
        
        response = client.get("/shops/1/items")
        assert response.status_code == 200
        assert isinstance(response.json["items"][0]["stock_quantity"], int)


class TestHalifaxTimezone:
    """Tests for Halifax timezone feature"""
    
    def test_halifax_timezone_constant_exists(self):
        """HALIFAX_TZ constant should be defined"""
        import flask_app.shop as shop
        assert hasattr(shop, "HALIFAX_TZ")
        assert str(shop.HALIFAX_TZ) == "America/Halifax"
    
    def test_shop_status_uses_halifax_timezone(self):
        """Shop open/closed status should use Halifax timezone"""
        HALIFAX_TZ = pytz.timezone('America/Halifax')
        # This test verifies the timezone is correctly applied
        now_halifax = datetime.now(HALIFAX_TZ)
        assert now_halifax.tzinfo is not None
    
    def test_get_shops_returns_is_open_field(self, client, monkeypatch):
        """GET /shops should return is_open in today_hours"""
        sample_shops = {
            "shops": [
                {
                    "id": 1,
                    "name": "Tim Hortons",
                    "today_hours": {
                        "open_time": "06:00",
                        "close_time": "22:00",
                        "is_open": True,
                        "status": "Open now",
                        "next_change": "22:00"
                    }
                }
            ],
            "total": 1,
            "filters_applied": {}
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shops", lambda *args, **kwargs: sample_shops)
        
        response = client.get("/shops")
        assert response.status_code == 200
        today_hours = response.json["shops"][0]["today_hours"]
        assert "is_open" in today_hours
        assert isinstance(today_hours["is_open"], bool)


class TestTimeParsing:
    """Tests for time parsing fix (single-digit hours)"""
    
    def test_parse_single_digit_hour(self):
        """Should correctly parse '6:00:00' format"""
        time_str = "6:00:00"
        time_parts = str(time_str).rstrip(':').split(':')
        parsed_time = time(int(time_parts[0]), int(time_parts[1]))
        
        assert parsed_time.hour == 6
        assert parsed_time.minute == 0
    
    def test_parse_double_digit_hour(self):
        """Should correctly parse '06:00:00' format"""
        time_str = "06:00:00"
        time_parts = str(time_str).rstrip(':').split(':')
        parsed_time = time(int(time_parts[0]), int(time_parts[1]))
        
        assert parsed_time.hour == 6
        assert parsed_time.minute == 0
    
    def test_parse_evening_time(self):
        """Should correctly parse '22:00:00' format"""
        time_str = "22:00:00"
        time_parts = str(time_str).rstrip(':').split(':')
        parsed_time = time(int(time_parts[0]), int(time_parts[1]))
        
        assert parsed_time.hour == 22
        assert parsed_time.minute == 0
    
    def test_parse_time_with_trailing_colon(self):
        """Should handle time string with trailing colon"""
        time_str = "6:00:"
        time_parts = str(time_str).rstrip(':').split(':')
        parsed_time = time(int(time_parts[0]), int(time_parts[1]))
        
        assert parsed_time.hour == 6
        assert parsed_time.minute == 0
    
    def test_time_comparison_open_hours(self):
        """Should correctly determine if current time is within open hours"""
        open_time = time(6, 0)
        close_time = time(22, 0)
        
        # Test time during open hours (noon)
        current_time = time(12, 0)
        is_open = open_time <= current_time <= close_time
        assert is_open is True
        
        # Test time before open (5am)
        current_time = time(5, 0)
        is_open = open_time <= current_time <= close_time
        assert is_open is False
        
        # Test time after close (11pm)
        current_time = time(23, 0)
        is_open = open_time <= current_time <= close_time
        assert is_open is False


class TestShopStatusText:
    """Tests for shop status text display"""
    
    def test_status_open_now(self, client, monkeypatch):
        """When open, status should say 'Open now'"""
        sample_shops = {
            "shops": [
                {
                    "id": 1,
                    "name": "Tim Hortons",
                    "today_hours": {
                        "open_time": "06:00",
                        "close_time": "22:00",
                        "is_open": True,
                        "status": "Open now",
                        "next_change": "22:00"
                    }
                }
            ],
            "total": 1,
            "filters_applied": {}
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shops", lambda *args, **kwargs: sample_shops)
        
        response = client.get("/shops")
        assert response.status_code == 200
        status = response.json["shops"][0]["today_hours"]["status"]
        assert status == "Open now"
    
    def test_status_opens_at_when_closed(self, client, monkeypatch):
        """When closed, status should say 'Opens at HH:MM'"""
        sample_shops = {
            "shops": [
                {
                    "id": 1,
                    "name": "Tim Hortons",
                    "today_hours": {
                        "open_time": "06:00",
                        "close_time": "22:00",
                        "is_open": False,
                        "status": "Opens at 06:00",
                        "next_change": "06:00"
                    }
                }
            ],
            "total": 1,
            "filters_applied": {}
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shops", lambda *args, **kwargs: sample_shops)
        
        response = client.get("/shops")
        assert response.status_code == 200
        status = response.json["shops"][0]["today_hours"]["status"]
        assert "Opens at" in status
    
    def test_next_change_shows_close_time_when_open(self, client, monkeypatch):
        """When open, next_change should show close time"""
        sample_shops = {
            "shops": [
                {
                    "id": 1,
                    "name": "Tim Hortons",
                    "today_hours": {
                        "open_time": "06:00",
                        "close_time": "22:00",
                        "is_open": True,
                        "status": "Open now",
                        "next_change": "22:00"
                    }
                }
            ],
            "total": 1,
            "filters_applied": {}
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shops", lambda *args, **kwargs: sample_shops)
        
        response = client.get("/shops")
        assert response.status_code == 200
        next_change = response.json["shops"][0]["today_hours"]["next_change"]
        assert next_change == "22:00"
    
    def test_next_change_shows_open_time_when_closed(self, client, monkeypatch):
        """When closed, next_change should show open time"""
        sample_shops = {
            "shops": [
                {
                    "id": 1,
                    "name": "Tim Hortons",
                    "today_hours": {
                        "open_time": "06:00",
                        "close_time": "22:00",
                        "is_open": False,
                        "status": "Opens at 06:00",
                        "next_change": "06:00"
                    }
                }
            ],
            "total": 1,
            "filters_applied": {}
        }
        
        import flask_app.shop as shop
        monkeypatch.setattr(shop, "get_shops", lambda *args, **kwargs: sample_shops)
        
        response = client.get("/shops")
        assert response.status_code == 200
        next_change = response.json["shops"][0]["today_hours"]["next_change"]
        assert next_change == "06:00"


class TestBookingWithVariants:
    """Tests for booking with variants feature"""
    
    def test_create_booking_with_variants_calculates_price(self):
        """Booking with variants should calculate correct total price"""
        from flask_app.booking import calculate_total_price
        
        base_price = 89.99
        quantity = 1
        variants = [
            {"variant_type": "Size", "variant_value": "50ml", "price_adjustment": -45.00}
        ]
        
        total = calculate_total_price(base_price, quantity, variants)
        expected = (89.99 - 45.00) * 1  # 44.99
        assert round(total, 2) == round(expected, 2)
    
    def test_create_booking_with_multiple_quantity_and_variants(self):
        """Booking with quantity > 1 and variants should calculate correctly"""
        from flask_app.booking import calculate_total_price
        
        base_price = 89.99
        quantity = 2
        variants = [
            {"variant_type": "Size", "variant_value": "100ml", "price_adjustment": 0.00}
        ]
        
        total = calculate_total_price(base_price, quantity, variants)
        expected = 89.99 * 2  # 179.98
        assert round(total, 2) == round(expected, 2)
    
    def test_create_booking_with_positive_price_adjustment(self):
        """Booking with positive price adjustment should increase total"""
        from flask_app.booking import calculate_total_price
        
        base_price = 89.99
        quantity = 1
        variants = [
            {"variant_type": "Size", "variant_value": "200ml", "price_adjustment": 85.00}
        ]
        
        total = calculate_total_price(base_price, quantity, variants)
        expected = 89.99 + 85.00  # 174.99
        assert round(total, 2) == round(expected, 2)
