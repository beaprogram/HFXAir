"""
Test suite for Booking API endpoints.
Following TDD approach - comprehensive test cases.
"""
import pytest
from unittest.mock import patch, MagicMock
import json
from flask_app.tests.test_constants import (
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
    PICKUP_CODE_LENGTH,
    TEST_SHOP_ID,
    TEST_ITEM_ID,
    TEST_USER_ID,
    TEST_USER_ID_ALT,
    TEST_BOOKING_ID,
    TEST_ID_NOT_FOUND_LARGE,
    TEST_QUANTITY_SINGLE,
    TEST_QUANTITY_DOUBLE,
    TEST_QUANTITY_TRIPLE,
    TEST_QUANTITY_INVALID,
    TEST_STOCK_FULL,
    TEST_STOCK_LOW,
    TEST_STOCK_EMPTY,
    TEST_BOOKING_TOTAL_BASIC,
    TEST_BOOKING_TOTAL_DOUBLE,
    TEST_PICKUP_CODE,
    TEST_PICKUP_CODE_ALT,
    TEST_PRICE_COFFEE
)


class TestBookingHelpers:
    """Tests for helper functions"""

    def test_generate_pickup_code_length(self):
        """Pickup code should be 6 characters"""
        from flask_app.booking import generate_pickup_code
        code = generate_pickup_code()
        assert len(code) == PICKUP_CODE_LENGTH

    def test_generate_pickup_code_alphanumeric(self):
        """Pickup code should contain only uppercase letters and digits"""
        from flask_app.booking import generate_pickup_code
        code = generate_pickup_code()
        assert code.isalnum()
        for char in code:
            assert char.isupper() or char.isdigit()

    def test_calculate_total_price_base_only(self):
        """Calculate price without variants"""
        from flask_app.booking import calculate_total_price
        base_price = 100.00
        quantity = TEST_QUANTITY_DOUBLE
        total = calculate_total_price(base_price, quantity, None)
        assert total == 200.00

    def test_calculate_total_price_with_variants(self):
        """Calculate price with variants"""
        from flask_app.booking import calculate_total_price
        base_price = 100.00
        variant_adjustment = 10.00
        variants = [
            {
                'variant_type': 'Size',
                'variant_value': 'Large',
                'price_adjustment': variant_adjustment
            }
        ]
        total = calculate_total_price(base_price, TEST_QUANTITY_DOUBLE, variants)
        assert total == 220.00  # (100 + 10) * 2

    def test_calculate_total_price_empty_variants(self):
        """Calculate price with empty variants list"""
        from flask_app.booking import calculate_total_price
        base_price = 50.00
        total = calculate_total_price(base_price, TEST_QUANTITY_TRIPLE, [])
        assert total == 150.00

    def test_get_availability_status_in_stock(self):
        """Stock > 5 should be in_stock"""
        from flask_app.booking import get_availability_status
        assert get_availability_status(TEST_STOCK_LOW) == 'in_stock'
        assert get_availability_status(PICKUP_CODE_LENGTH) == 'in_stock'

    def test_get_availability_status_low_stock(self):
        """Stock 1-5 should be low_stock"""
        from flask_app.booking import get_availability_status
        from flask_app.constants import LOW_STOCK_THRESHOLD
        assert get_availability_status(LOW_STOCK_THRESHOLD) == 'low_stock'
        assert get_availability_status(TEST_QUANTITY_SINGLE) == 'low_stock'

    def test_get_availability_status_out_of_stock(self):
        """Stock 0 or negative should be out_of_stock"""
        from flask_app.booking import get_availability_status
        assert get_availability_status(TEST_STOCK_EMPTY) == 'out_of_stock'
        assert get_availability_status(-1) == 'out_of_stock'


class TestGetBookingsAPI:
    """Tests for GET /bookings endpoint"""

    def test_get_bookings_requires_user_id(self, client):
        """GET /bookings without user_id returns 401"""
        response = client.get("/bookings")
        assert response.status_code == HTTP_UNAUTHORIZED
        assert response.json["error"] == "Unauthorized"

    def test_get_bookings_invalid_user_id(self, client):
        """GET /bookings with invalid user_id returns 400"""
        response = client.get("/bookings?user_id=abc")
        assert response.status_code == HTTP_BAD_REQUEST
        assert response.json["error"] == "Invalid user_id"

    def test_get_bookings_success(self, client, monkeypatch):
        """GET /bookings returns user bookings"""
        mock_bookings = {
            'success': True,
            'bookings': [
                {
                    'id': TEST_BOOKING_ID,
                    'user_id': TEST_USER_ID,
                    'item_id': TEST_ITEM_ID,
                    'shop_id': TEST_SHOP_ID,
                    'quantity': TEST_QUANTITY_SINGLE,
                    'total_price': TEST_BOOKING_TOTAL_BASIC,
                    'status': 'active',
                    'pickup_code': TEST_PICKUP_CODE
                }
            ]
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "get_user_bookings",
            lambda user_id, status=None: mock_bookings
        )

        response = client.get(f"/bookings?user_id={TEST_USER_ID}")
        assert response.status_code == HTTP_OK
        assert "bookings" in response.json
        assert len(response.json["bookings"]) == TEST_QUANTITY_SINGLE

    def test_get_bookings_filter_by_status(self, client, monkeypatch):
        """GET /bookings?status=active filters by status"""
        mock_bookings = {
            'success': True,
            'bookings': [
                {'id': TEST_BOOKING_ID, 'status': 'active'}
            ]
        }

        import flask_app.booking as booking

        def mock_get_bookings(user_id, status=None):
            assert status == 'active'
            return mock_bookings

        monkeypatch.setattr(booking, "get_user_bookings", mock_get_bookings)

        response = client.get(f"/bookings?user_id={TEST_USER_ID}&status=active")
        assert response.status_code == HTTP_OK


class TestCreateBookingAPI:
    """Tests for POST /bookings endpoint"""

    def test_create_booking_requires_body(self, client):
        """POST /bookings without body returns 400"""
        response = client.post("/bookings", content_type='application/json')
        assert response.status_code == HTTP_BAD_REQUEST

    def test_create_booking_requires_user_id(self, client):
        """POST /bookings without user_id returns 401"""
        response = client.post("/bookings", json={
            "item_id": TEST_ITEM_ID,
            "shop_id": TEST_SHOP_ID,
            "quantity": TEST_QUANTITY_SINGLE
        })
        assert response.status_code == HTTP_UNAUTHORIZED

    def test_create_booking_requires_item_and_shop(self, client):
        """POST /bookings without item_id/shop_id returns 400"""
        response = client.post("/bookings", json={
            "user_id": TEST_USER_ID,
            "quantity": TEST_QUANTITY_SINGLE
        })
        assert response.status_code == HTTP_BAD_REQUEST
        assert "item_id and shop_id are required" in response.json["message"]

    def test_create_booking_success(self, client, monkeypatch):
        """POST /bookings creates new booking"""
        mock_result = {
            'success': True,
            'booking': {
                'id': TEST_BOOKING_ID,
                'user_id': TEST_USER_ID,
                'item_id': TEST_ITEM_ID,
                'shop_id': TEST_SHOP_ID,
                'quantity': TEST_QUANTITY_DOUBLE,
                'total_price': TEST_BOOKING_TOTAL_DOUBLE,
                'status': 'active',
                'pickup_code': TEST_PICKUP_CODE_ALT
            }
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "create_booking",
            lambda user_id, item_id, shop_id, quantity, selected_variants=None: mock_result
        )

        response = client.post("/bookings", json={
            "user_id": TEST_USER_ID,
            "item_id": TEST_ITEM_ID,
            "shop_id": TEST_SHOP_ID,
            "quantity": TEST_QUANTITY_DOUBLE
        })

        assert response.status_code == HTTP_CREATED
        assert response.json["status"] == "active"
        assert response.json["pickup_code"] == TEST_PICKUP_CODE_ALT

    def test_create_booking_invalid_quantity(self, client, monkeypatch):
        """POST /bookings with quantity > 3 returns 400"""
        mock_result = {
            'success': False,
            'error': 'Invalid quantity',
            'message': 'Quantity must be between 1 and 3'
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "create_booking",
            lambda user_id, item_id, shop_id, quantity, selected_variants=None: mock_result
        )

        response = client.post("/bookings", json={
            "user_id": TEST_USER_ID,
            "item_id": TEST_ITEM_ID,
            "shop_id": TEST_SHOP_ID,
            "quantity": TEST_QUANTITY_INVALID
        })

        assert response.status_code == HTTP_BAD_REQUEST
        assert response.json["error"] == "Invalid quantity"

    def test_create_booking_out_of_stock(self, client, monkeypatch):
        """POST /bookings for out of stock item returns 400"""
        mock_result = {
            'success': False,
            'error': 'Out of stock',
            'message': 'This item is currently out of stock'
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "create_booking",
            lambda user_id, item_id, shop_id, quantity, selected_variants=None: mock_result
        )

        response = client.post("/bookings", json={
            "user_id": TEST_USER_ID,
            "item_id": TEST_ITEM_ID,
            "shop_id": TEST_SHOP_ID,
            "quantity": TEST_QUANTITY_SINGLE
        })

        assert response.status_code == HTTP_BAD_REQUEST
        assert response.json["error"] == "Out of stock"

    def test_create_booking_item_not_found(self, client, monkeypatch):
        """POST /bookings with invalid item_id returns 404"""
        mock_result = {
            'success': False,
            'error': 'Not found',
            'message': 'Item not found'
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "create_booking",
            lambda user_id, item_id, shop_id, quantity, selected_variants=None: mock_result
        )

        response = client.post("/bookings", json={
            "user_id": TEST_USER_ID,
            "item_id": TEST_ID_NOT_FOUND_LARGE,
            "shop_id": TEST_SHOP_ID,
            "quantity": TEST_QUANTITY_SINGLE
        })

        assert response.status_code == HTTP_NOT_FOUND

    def test_create_booking_already_reserved(self, client, monkeypatch):
        """POST /bookings for already reserved item returns 400"""
        mock_result = {
            'success': False,
            'error': 'Already reserved',
            'message': 'You already have an active reservation for this item'
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "create_booking",
            lambda user_id, item_id, shop_id, quantity, selected_variants=None: mock_result
        )

        response = client.post("/bookings", json={
            "user_id": TEST_USER_ID,
            "item_id": TEST_ITEM_ID,
            "shop_id": TEST_SHOP_ID,
            "quantity": TEST_QUANTITY_SINGLE
        })

        assert response.status_code == HTTP_BAD_REQUEST
        assert response.json["error"] == "Already reserved"


class TestCancelBookingAPI:
    """Tests for POST /bookings/<id>/cancel endpoint"""

    def test_cancel_booking_requires_user_id(self, client):
        """POST /bookings/<id>/cancel without user_id returns 401"""
        response = client.post(f"/bookings/{TEST_BOOKING_ID}/cancel", json={})
        assert response.status_code == HTTP_UNAUTHORIZED

    def test_cancel_booking_success(self, client, monkeypatch):
        """POST /bookings/<id>/cancel cancels booking"""
        mock_result = {
            'success': True,
            'booking': {
                'id': TEST_BOOKING_ID,
                'status': 'cancelled',
                'cancelled_at': '2025-12-03T22:00:00Z'
            }
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "cancel_booking",
            lambda booking_id, user_id: mock_result
        )

        response = client.post(
            f"/bookings/{TEST_BOOKING_ID}/cancel",
            json={"user_id": TEST_USER_ID}
        )

        assert response.status_code == HTTP_OK
        assert response.json["status"] == "cancelled"

    def test_cancel_booking_not_found(self, client, monkeypatch):
        """POST /bookings/<id>/cancel for invalid id returns 404"""
        mock_result = {
            'success': False,
            'error': 'Not found',
            'message': 'Reservation not found'
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "cancel_booking",
            lambda booking_id, user_id: mock_result
        )

        response = client.post(
            f"/bookings/{TEST_ID_NOT_FOUND_LARGE}/cancel",
            json={"user_id": TEST_USER_ID}
        )

        assert response.status_code == HTTP_NOT_FOUND

    def test_cancel_booking_forbidden(self, client, monkeypatch):
        """POST /bookings/<id>/cancel by different user returns 403"""
        mock_result = {
            'success': False,
            'error': 'Forbidden',
            'message': "You don't have permission to cancel this reservation"
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "cancel_booking",
            lambda booking_id, user_id: mock_result
        )

        response = client.post(
            f"/bookings/{TEST_BOOKING_ID}/cancel",
            json={"user_id": TEST_USER_ID_ALT}
        )

        assert response.status_code == HTTP_FORBIDDEN

    def test_cancel_booking_already_cancelled(self, client, monkeypatch):
        """POST /bookings/<id>/cancel for cancelled booking returns 400"""
        mock_result = {
            'success': False,
            'error': 'Already cancelled',
            'message': 'This reservation has already been cancelled'
        }

        import flask_app.booking as booking
        monkeypatch.setattr(
            booking, "cancel_booking",
            lambda booking_id, user_id: mock_result
        )

        response = client.post(
            f"/bookings/{TEST_BOOKING_ID}/cancel",
            json={"user_id": TEST_USER_ID}
        )

        assert response.status_code == HTTP_BAD_REQUEST
        assert response.json["error"] == "Already cancelled"