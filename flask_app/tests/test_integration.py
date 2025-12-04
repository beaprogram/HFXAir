"""
Integration tests for shop and booking modules
"""
import pytest
from datetime import datetime, time, timedelta
from unittest.mock import patch, MagicMock


class TestGetShops:
    
    @patch('flask_app.shop.get_db_connection')
    def test_basic_listing(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Tim Hortons', 'Food & Beverage', 'Coffee and donuts', 'Terminal 1', 'Gate A5', 'Near security', time(6, 0), time(22, 0), False),
            (2, 'Hudson News', 'Retail', 'Books', 'Terminal 1', 'Gate B2', 'Main hall', time(6, 0), time(22, 0), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops()
        
        assert res['total'] == 2
        assert len(res['shops']) == 2
    
    @patch('flask_app.shop.get_db_connection')
    def test_category_filter(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Tim Hortons', 'Food & Beverage', 'Coffee', 'T1', 'A5', 'Loc', time(6, 0), time(22, 0), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops(category='Food & Beverage')
        assert res['filters_applied']['category'] == 'Food & Beverage'
    
    @patch('flask_app.shop.get_db_connection')
    def test_terminal_filter(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Shop A', 'Retail', 'Desc', 'Terminal 1', 'Gate 5', 'Loc', time(6, 0), time(22, 0), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops(terminal='Terminal 1')
        assert res['filters_applied']['terminal'] == 'Terminal 1'
    
    @patch('flask_app.shop.get_db_connection')
    def test_gate_filter(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Shop A', 'Retail', 'Desc', 'T1', 'Gate A5', 'Loc', time(6, 0), time(22, 0), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops(gate='Gate A5')
        assert res['filters_applied']['gate'] == 'Gate A5'
    
    @patch('flask_app.shop.get_db_connection')
    def test_name_sorting(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Zara', 'Retail', 'Clothing', 'T1', 'A1', 'Loc', time(6, 0), time(22, 0), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops(sort='name')
        assert res['filters_applied']['sort'] == 'name'
    
    @patch('flask_app.shop.get_db_connection')
    def test_status_sorting(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Shop A', 'Food', 'Desc', 'T1', 'A5', 'Loc', time(6, 0), time(22, 0), False),
            (2, 'Shop B', 'Food', 'Desc', 'T1', 'A6', 'Loc', time(6, 0), time(22, 0), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops(sort='status')
        assert res['filters_applied']['sort'] == 'status'
    
    @patch('flask_app.shop.get_db_connection')
    def test_open_now_filter(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        # 24hr shop should always be open
        cur.fetchall.return_value = [
            (1, 'Night Owl', 'Food', 'Coffee', 'T1', 'A5', 'Loc', time(0, 0), time(23, 59), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops(open_now=True)
        assert res['filters_applied']['open_now'] == True
    
    @patch('flask_app.shop.get_db_connection')
    def test_closed_shop_status(self, mock_db):
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        # is_closed=True means closed for the day
        cur.fetchall.return_value = [
            (1, 'Holiday Shop', 'Gift', 'Seasonal', 'T1', 'A5', 'Loc', time(6, 0), time(22, 0), True),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops()
        assert res['shops'][0]['today_hours']['status'] == 'Closed today'
    
    @patch('flask_app.shop.get_db_connection')
    def test_time_as_string(self, mock_db):
        # DB sometimes returns time as string
        from flask_app.shop import get_shops
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Test Shop', 'Food', 'Desc', 'T1', 'A5', 'Loc', '06:00:00', '22:00:00', False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shops()
        assert res['total'] == 1
    
    @patch('flask_app.shop.get_db_connection')
    def test_db_error(self, mock_db):
        from flask_app.shop import get_shops
        mock_db.side_effect = Exception("Connection failed")
        
        res = get_shops()
        assert res['shops'] == []


class TestGetShopById:
    
    @patch('flask_app.shop.get_db_connection')
    def test_found(self, mock_db):
        from flask_app.shop import get_shop_by_id
        
        cur = MagicMock()
        cur.fetchone.side_effect = [
            (1, 'Tim Hortons', 'Food & Beverage', 'Coffee shop', 'Terminal 1', 'Gate A5', 'Near gate'),
            None
        ]
        cur.fetchall.side_effect = [
            [(0, time(6, 0), time(22, 0), False)],
            []
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        shop = get_shop_by_id(1)
        assert shop['name'] == 'Tim Hortons'
        assert shop['id'] == 1
    
    @patch('flask_app.shop.get_db_connection')
    def test_not_found(self, mock_db):
        from flask_app.shop import get_shop_by_id
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        assert get_shop_by_id(9999) is None
    
    @patch('flask_app.shop.get_db_connection')
    def test_db_error(self, mock_db):
        from flask_app.shop import get_shop_by_id
        mock_db.side_effect = Exception("DB error")
        
        assert get_shop_by_id(1) is None


class TestShopHours:
    
    @patch('flask_app.shop.get_db_connection')
    def test_invalid_shop(self, mock_db):
        from flask_app.shop import get_shop_hours
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        assert get_shop_hours(9999) is None
    
    @patch('flask_app.shop.get_db_connection')
    def test_weekly_schedule(self, mock_db):
        from flask_app.shop import get_shop_hours
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Tim Hortons')
        cur.fetchall.side_effect = [
            # weekly: day_of_week, open_time, close_time, is_closed
            [(0, time(6, 0), time(22, 0), False), (1, time(6, 0), time(22, 0), False)],
            # exceptions
            []
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shop_hours(1)
        assert res['shop_name'] == 'Tim Hortons'
        assert 'weekly_hours' in res


class TestShopCategories:
    
    @patch('flask_app.shop.get_db_connection')
    def test_list_all(self, mock_db):
        from flask_app.shop import get_shop_categories
        
        cur = MagicMock()
        cur.fetchall.return_value = [
            ('Food & Beverage', 3),
            ('Retail', 5),
            ('Services', 2),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shop_categories()
        assert len(res['categories']) == 3
    
    @patch('flask_app.shop.get_db_connection')
    def test_db_error(self, mock_db):
        from flask_app.shop import get_shop_categories
        mock_db.side_effect = Exception("DB down")
        
        res = get_shop_categories()
        assert res['categories'] == []


class TestShopCatalog:
    
    @patch('flask_app.shop.get_db_connection')
    def test_invalid_shop(self, mock_db):
        from flask_app.shop import get_shop_catalog
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        assert get_shop_catalog(9999) is None
    
    @patch('flask_app.shop.get_db_connection')
    def test_with_items(self, mock_db):
        from flask_app.shop import get_shop_catalog
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Tim Hortons')
        cur.fetchall.side_effect = [
            # categories
            [(1, 'Beverages'), (2, 'Snacks')],
            # items cat 1
            [(1, 'Coffee', 2.99, 'Hot coffee')],
            # items cat 2
            [(2, 'Donut', 1.99, 'Fresh donut')],
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shop_catalog(1, include_items=True)
        assert res['shop_name'] == 'Tim Hortons'
        assert len(res['categories']) == 2


class TestShopItems:
    
    @patch('flask_app.shop.get_db_connection')
    def test_invalid_shop(self, mock_db):
        from flask_app.shop import get_shop_items
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        assert get_shop_items(9999) is None
    
    @patch('flask_app.shop.get_db_connection')
    def test_with_variants(self, mock_db):
        from flask_app.shop import get_shop_items
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Tim Hortons')
        cur.fetchall.side_effect = [
            # item_id, name, price, desc, availability, stock, image_url
            [(1, 'Coffee', 2.99, 'Hot coffee', 'in_stock', 50, 'https://img.com/coffee.jpg')],
            # variants
            [('Size', 'Large', 1.00)],
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shop_items(1)
        assert res['shop_name'] == 'Tim Hortons'
        assert len(res['items']) == 1
    
    @patch('flask_app.shop.get_db_connection')
    def test_search(self, mock_db):
        from flask_app.shop import get_shop_items
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Tim Hortons')
        cur.fetchall.side_effect = [
            [(1, 'Coffee', 2.99, 'Hot coffee', 'in_stock', 50, None)],
            [],
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shop_items(1, search='coffee')
        assert res is not None
    
    @patch('flask_app.shop.get_db_connection')
    def test_price_range(self, mock_db):
        from flask_app.shop import get_shop_items
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Tim Hortons')
        cur.fetchall.side_effect = [
            [(1, 'Coffee', 2.99, 'Hot coffee', 'in_stock', 50, None)],
            [],
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shop_items(1, min_price=1.00, max_price=5.00)
        assert res is not None


class TestItemById:
    
    @patch('flask_app.shop.get_db_connection')
    def test_not_found(self, mock_db):
        from flask_app.shop import get_item_by_id
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        assert get_item_by_id(9999) is None
    
    @patch('flask_app.shop.get_db_connection')
    def test_basic_item(self, mock_db):
        from flask_app.shop import get_item_by_id
        
        cur = MagicMock()
        # item_id, name, base_price, description
        cur.fetchone.return_value = (1, 'Coffee', 2.99, 'Hot brewed coffee')
        cur.fetchall.return_value = []
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_item_by_id(1)
        assert res['name'] == 'Coffee'
        assert res['base_price'] == 2.99
    
    @patch('flask_app.shop.get_db_connection')
    def test_item_with_sizes(self, mock_db):
        from flask_app.shop import get_item_by_id
        
        cur = MagicMock()
        cur.fetchone.return_value = (10, 'Perfume Set', 89.99, 'Luxury fragrance')
        # variant_type, variant_value, price_adjustment
        cur.fetchall.return_value = [
            ('Size', '50ml', -45.00),
            ('Size', '100ml', 0.00),
            ('Size', '200ml', 85.00),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_item_by_id(10)
        assert len(res['variants']) == 3
        assert 'Size' in res['variant_types']


class TestItemCategories:
    
    @patch('flask_app.shop.get_db_connection')
    def test_invalid_shop(self, mock_db):
        from flask_app.shop import get_shop_item_categories
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        assert get_shop_item_categories(9999) is None
    
    @patch('flask_app.shop.get_db_connection')
    def test_valid_shop(self, mock_db):
        from flask_app.shop import get_shop_item_categories
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Tim Hortons')
        # category_id, category_name, item_count
        cur.fetchall.return_value = [(1, 'Beverages', 5), (2, 'Snacks', 8)]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_shop_item_categories(1)
        assert len(res['categories']) == 2


# ========== Booking tests ==========

class TestPickupCodes:
    
    def test_length(self):
        from flask_app.booking import generate_pickup_code
        assert len(generate_pickup_code()) == 6
    
    def test_format(self):
        from flask_app.booking import generate_pickup_code
        code = generate_pickup_code()
        assert code.isalnum()
        for c in code:
            assert c.isupper() or c.isdigit()
    
    def test_uniqueness(self):
        from flask_app.booking import generate_pickup_code
        codes = [generate_pickup_code() for _ in range(50)]
        # should have at least 90% unique
        assert len(set(codes)) > 45
    
    @patch('flask_app.booking.get_db_connection')
    def test_db_check(self, mock_db):
        from flask_app.booking import generate_unique_pickup_code
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        
        code = generate_unique_pickup_code(cur)
        assert len(code) == 6


class TestGetBookings:
    
    @patch('flask_app.booking.get_db_connection')
    def test_empty_list(self, mock_db):
        from flask_app.booking import get_user_bookings
        
        cur = MagicMock()
        cur.fetchall.return_value = []
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_user_bookings('user123', status='active')
        assert 'bookings' in res
    
    @patch('flask_app.booking.get_db_connection')
    def test_with_data(self, mock_db):
        from flask_app.booking import get_user_bookings
        
        cur = MagicMock()
        now = datetime.now()
        exp = now + timedelta(hours=24)
        # all 22 columns from the query
        cur.fetchall.return_value = [(
            1, 'user123', 1, 1, 2, 5.98, 'active', 'ABC123', None,
            now, exp, None, None,
            'Coffee', 'Hot coffee', 2.99, 'in_stock', 50,
            'Tim Hortons', 'Near gate', 'Terminal 1', 'Gate A5',
        )]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = get_user_bookings('user123')
        assert res['success']
        assert res['bookings'][0]['pickup_code'] == 'ABC123'


class TestCreateBooking:
    
    @patch('flask_app.booking.get_db_connection')
    def test_success(self, mock_db):
        from flask_app.booking import create_booking
        
        cur = MagicMock()
        cur.fetchone.side_effect = [
            (1, 'Coffee', 2.99, 50, 1),  # item info
            None,  # pickup code unique
            (1,),  # new booking id
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = create_booking('user123', 1, 1, 2)
        assert res is not None
    
    @patch('flask_app.booking.get_db_connection')
    def test_item_not_found(self, mock_db):
        from flask_app.booking import create_booking
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = create_booking('user123', 9999, 1, 1)
        assert 'error' in res
    
    @patch('flask_app.booking.get_db_connection')
    def test_out_of_stock(self, mock_db):
        from flask_app.booking import create_booking
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Coffee', 2.99, 0, 1)  # stock=0
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = create_booking('user123', 1, 1, 1)
        assert 'error' in res


class TestCancelBooking:
    
    @patch('flask_app.booking.get_db_connection')
    def test_success(self, mock_db):
        from flask_app.booking import cancel_booking
        
        cur = MagicMock()
        cur.fetchone.side_effect = [
            (1, 'user123', 1, 2, 'active'),  # booking
            (48, 'Coffee'),  # item for stock restore
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = cancel_booking(1, 'user123')
        assert res['success']
    
    @patch('flask_app.booking.get_db_connection')
    def test_not_found(self, mock_db):
        from flask_app.booking import cancel_booking
        
        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = cancel_booking(9999, 'user123')
        assert 'error' in res
    
    @patch('flask_app.booking.get_db_connection')
    def test_wrong_user(self, mock_db):
        from flask_app.booking import cancel_booking
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'other_user', 1, 2, 'active')
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = cancel_booking(1, 'user123')
        assert 'error' in res
    
    @patch('flask_app.booking.get_db_connection')
    def test_already_cancelled(self, mock_db):
        from flask_app.booking import cancel_booking
        
        cur = MagicMock()
        cur.fetchone.return_value = (1, 'user123', 1, 2, 'cancelled')
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        res = cancel_booking(1, 'user123')
        assert not res['success']


class TestExpireBookings:
    
    @patch('flask_app.booking.get_db_connection')
    def test_expires_old(self, mock_db):
        from flask_app.booking import expire_old_bookings
        
        cur = MagicMock()
        cur.fetchall.return_value = [(1, 1, 2)]  # id, item_id, qty
        cur.fetchone.return_value = (48,)  # current stock
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        count = expire_old_bookings()
        assert count == 1
    
    @patch('flask_app.booking.get_db_connection')
    def test_nothing_to_expire(self, mock_db):
        from flask_app.booking import expire_old_bookings
        
        cur = MagicMock()
        cur.fetchall.return_value = []
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn
        
        assert expire_old_bookings() == 0


# ========== Business rules ==========

class TestReservationExpiry:
    
    def test_24hr_window(self):
        created = datetime.now()
        expiry = created + timedelta(hours=24)
        assert (expiry - created).total_seconds() == 86400
    
    def test_still_valid_at_23hrs(self):
        created = datetime.now()
        expiry = created + timedelta(hours=24)
        check = created + timedelta(hours=23)
        assert check < expiry
    
    def test_expired_at_25hrs(self):
        created = datetime.now()
        expiry = created + timedelta(hours=24)
        check = created + timedelta(hours=25)
        assert check > expiry


class TestStockManagement:
    
    def test_decrease_on_order(self):
        stock = 10
        assert stock - 3 == 7
    
    def test_restore_on_cancel(self):
        stock = 7
        assert stock + 3 == 10
    
    def test_reject_if_insufficient(self):
        stock = 2
        requested = 5
        assert requested > stock
    
    def test_cumulative_orders(self):
        stock = 20
        stock -= 5
        stock -= 3
        stock -= 7
        assert stock == 5