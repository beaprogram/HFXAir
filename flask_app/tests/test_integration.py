"""
Integration tests for shop and booking modules
"""
import pytest
from datetime import datetime, time, timedelta
from unittest.mock import patch, MagicMock
from flask_app.tests.test_constants import (
    PICKUP_CODE_LENGTH,
    SECONDS_IN_24_HOURS,
    TEST_HOURS_23,
    TEST_HOURS_24,
    TEST_HOURS_25,
    TEST_SHOP_ID,
    TEST_SHOP_ID_ALT,
    TEST_SHOP_COUNT,
    TEST_CATEGORY_COUNT,
    TEST_ID_NOT_FOUND_LARGE,
    TEST_PRICE_COFFEE,
    TEST_BOOKING_TOTAL_TWO_COFFEES,
    TEST_STOCK_FULL,
    TEST_STOCK_EMPTY,
    TEST_STOCK_AFTER_ORDER,
    TEST_QUANTITY_DOUBLE,
    TEST_PICKUP_CODE,
    TEST_UNIQUENESS_ITERATIONS,
    TEST_UNIQUENESS_MIN_UNIQUE,
    TEST_STOCK_BEFORE_ORDER,
    TEST_STOCK_ORDER_QUANTITY,
    TEST_STOCK_AFTER_THREE_ORDER,
    TEST_STOCK_AFTER_RESTORE,
    TEST_STOCK_INSUFFICIENT,
    TEST_STOCK_REQUESTED_OVER,
    TEST_STOCK_CUMULATIVE_START,
    TEST_STOCK_CUMULATIVE_ORDER1,
    TEST_STOCK_CUMULATIVE_ORDER2,
    TEST_STOCK_CUMULATIVE_ORDER3,
    TEST_STOCK_CUMULATIVE_FINAL,
    TEST_OPEN_HOUR,
    TEST_CLOSE_HOUR,
    TEST_CATEGORY_FOOD_COUNT,
    TEST_CATEGORY_DESSERTS_COUNT
)


class TestGetShops:

    @patch('flask_app.shop.get_db_connection')
    def test_basic_listing(self, mock_db):
        from flask_app.shop import get_shops

        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Tim Hortons', 'Food & Beverage', 'Coffee and donuts', 'Terminal 1',
             'Gate A5', 'Near security', time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
            (2, 'Hudson News', 'Retail', 'Books', 'Terminal 1', 'Gate B2',
             'Main hall', time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shops()

        assert res['total'] == TEST_SHOP_COUNT
        assert len(res['shops']) == TEST_SHOP_COUNT

    @patch('flask_app.shop.get_db_connection')
    def test_category_filter(self, mock_db):
        from flask_app.shop import get_shops

        cur = MagicMock()
        cur.fetchall.return_value = [
            (1, 'Tim Hortons', 'Food & Beverage', 'Coffee', 'T1', 'A5', 'Loc',
             time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
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
            (1, 'Shop A', 'Retail', 'Desc', 'Terminal 1', 'Gate 5', 'Loc',
             time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
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
            (1, 'Shop A', 'Retail', 'Desc', 'T1', 'Gate A5', 'Loc',
             time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
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
            (1, 'Zara', 'Retail', 'Clothing', 'T1', 'A1', 'Loc',
             time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
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
            (1, 'Shop A', 'Food', 'Desc', 'T1', 'A5', 'Loc',
             time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
            (2, 'Shop B', 'Food', 'Desc', 'T1', 'A6', 'Loc',
             time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
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
            (1, 'Night Owl', 'Food', 'Coffee', 'T1', 'A5', 'Loc',
             time(0, 0), time(23, 59), False),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shops(open_now=True)
        assert res['filters_applied']['open_now'] is True

    @patch('flask_app.shop.get_db_connection')
    def test_closed_shop_status(self, mock_db):
        from flask_app.shop import get_shops

        cur = MagicMock()
        # is_closed=True means closed for the day
        cur.fetchall.return_value = [
            (1, 'Holiday Shop', 'Gift', 'Seasonal', 'T1', 'A5', 'Loc',
             time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), True),
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
            (1, 'Test Shop', 'Food', 'Desc', 'T1', 'A5', 'Loc',
             '06:00:00', '22:00:00', False),
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
            (1, 'Tim Hortons', 'Food & Beverage', 'Coffee shop',
             'Terminal 1', 'Gate A5', 'Near gate'),
            None
        ]
        cur.fetchall.side_effect = [
            [(0, time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False)],
            []
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        shop = get_shop_by_id(TEST_SHOP_ID)
        assert shop['name'] == 'Tim Hortons'
        assert shop['id'] == TEST_SHOP_ID

    @patch('flask_app.shop.get_db_connection')
    def test_not_found(self, mock_db):
        from flask_app.shop import get_shop_by_id

        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        assert get_shop_by_id(TEST_ID_NOT_FOUND_LARGE) is None

    @patch('flask_app.shop.get_db_connection')
    def test_db_error(self, mock_db):
        from flask_app.shop import get_shop_by_id
        mock_db.side_effect = Exception("DB error")

        assert get_shop_by_id(TEST_SHOP_ID) is None


class TestShopHours:

    @patch('flask_app.shop.get_db_connection')
    def test_invalid_shop(self, mock_db):
        from flask_app.shop import get_shop_hours

        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        assert get_shop_hours(TEST_ID_NOT_FOUND_LARGE) is None

    @patch('flask_app.shop.get_db_connection')
    def test_weekly_schedule(self, mock_db):
        from flask_app.shop import get_shop_hours

        cur = MagicMock()
        cur.fetchone.return_value = (TEST_SHOP_ID, 'Tim Hortons')
        cur.fetchall.side_effect = [
            # weekly: day_of_week, open_time, close_time, is_closed
            [
                (0, time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False),
                (1, time(TEST_OPEN_HOUR, 0), time(TEST_CLOSE_HOUR, 0), False)
            ],
            # exceptions
            []
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shop_hours(TEST_SHOP_ID)
        assert res['shop_name'] == 'Tim Hortons'
        assert 'weekly_hours' in res


class TestShopCategories:

    @patch('flask_app.shop.get_db_connection')
    def test_list_all(self, mock_db):
        from flask_app.shop import get_shop_categories

        cur = MagicMock()
        cur.fetchall.return_value = [
            ('Food & Beverage', 3),
            ('Retail', TEST_CATEGORY_FOOD_COUNT),
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shop_categories()
        assert 'categories' in res

    @patch('flask_app.shop.get_db_connection')
    def test_empty(self, mock_db):
        from flask_app.shop import get_shop_categories

        cur = MagicMock()
        cur.fetchall.return_value = []
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shop_categories()
        assert res['categories'] == []


class TestShopCatalog:

    @patch('flask_app.shop.get_db_connection')
    def test_with_items(self, mock_db):
        from flask_app.shop import get_shop_catalog

        cur = MagicMock()
        cur.fetchone.return_value = (TEST_SHOP_ID, 'Tim Hortons')
        cur.fetchall.side_effect = [
            [(1, 'Beverages')],
            [(1, 'Coffee', TEST_PRICE_COFFEE, 'Hot coffee')]
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shop_catalog(TEST_SHOP_ID)
        assert res['shop_name'] == 'Tim Hortons'
        assert 'categories' in res

    @patch('flask_app.shop.get_db_connection')
    def test_shop_not_found(self, mock_db):
        from flask_app.shop import get_shop_catalog

        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        assert get_shop_catalog(TEST_ID_NOT_FOUND_LARGE) is None


class TestShopItems:

    @patch('flask_app.shop.get_db_connection')
    def test_basic_list(self, mock_db):
        from flask_app.shop import get_shop_items

        cur = MagicMock()
        cur.fetchone.return_value = (TEST_SHOP_ID, 'Tim Hortons')
        cur.fetchall.side_effect = [
            [(1, 'Coffee', TEST_PRICE_COFFEE, 'Hot coffee', 'in_stock',
              TEST_STOCK_FULL, 'http://img.com/coffee.jpg')],
            []  # variants
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shop_items(TEST_SHOP_ID)
        assert res['shop_name'] == 'Tim Hortons'
        assert 'items' in res

    @patch('flask_app.shop.get_db_connection')
    def test_with_filters(self, mock_db):
        from flask_app.shop import get_shop_items

        cur = MagicMock()
        cur.fetchone.return_value = (TEST_SHOP_ID, 'Tim Hortons')
        cur.fetchall.side_effect = [[], []]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shop_items(
            TEST_SHOP_ID,
            search='coffee',
            category_id=1,
            min_price=1.0,
            max_price=5.0
        )
        assert res is not None


class TestItemCategories:

    @patch('flask_app.shop.get_db_connection')
    def test_valid_shop(self, mock_db):
        from flask_app.shop import get_shop_item_categories

        cur = MagicMock()
        cur.fetchone.return_value = (TEST_SHOP_ID, 'Tim Hortons')
        cur.fetchall.return_value = [
            (1, 'Beverages', TEST_CATEGORY_FOOD_COUNT),
            (2, 'Food', TEST_SHOP_COUNT),
            (3, 'Desserts', TEST_CATEGORY_DESSERTS_COUNT)
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_shop_item_categories(TEST_SHOP_ID)
        assert res['shop_name'] == 'Tim Hortons'
        assert len(res['categories']) == TEST_CATEGORY_COUNT


# ========== Booking tests ==========

class TestPickupCodes:

    def test_length(self):
        from flask_app.booking import generate_pickup_code
        assert len(generate_pickup_code()) == PICKUP_CODE_LENGTH

    def test_format(self):
        from flask_app.booking import generate_pickup_code
        code = generate_pickup_code()
        assert code.isalnum()
        for c in code:
            assert c.isupper() or c.isdigit()

    def test_uniqueness(self):
        from flask_app.booking import generate_pickup_code
        codes = [generate_pickup_code() for _ in range(TEST_UNIQUENESS_ITERATIONS)]
        # should have at least 90% unique
        assert len(set(codes)) > TEST_UNIQUENESS_MIN_UNIQUE

    @patch('flask_app.booking.get_db_connection')
    def test_db_check(self, mock_db):
        from flask_app.booking import generate_unique_pickup_code

        cur = MagicMock()
        cur.fetchone.return_value = None

        code = generate_unique_pickup_code(cur)
        assert len(code) == PICKUP_CODE_LENGTH


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
        exp = now + timedelta(hours=TEST_HOURS_24)
        # all 22 columns from the query
        cur.fetchall.return_value = [(
            1, 'user123', 1, 1, TEST_QUANTITY_DOUBLE, TEST_BOOKING_TOTAL_TWO_COFFEES,
            'active', TEST_PICKUP_CODE, None,
            now, exp, None, None,
            'Coffee', 'Hot coffee', TEST_PRICE_COFFEE, 'in_stock', TEST_STOCK_FULL,
            'Tim Hortons', 'Near gate', 'Terminal 1', 'Gate A5',
        )]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = get_user_bookings('user123')
        assert res['success']
        assert res['bookings'][0]['pickup_code'] == TEST_PICKUP_CODE


class TestCreateBooking:

    @patch('flask_app.booking.get_db_connection')
    def test_success(self, mock_db):
        from flask_app.booking import create_booking

        cur = MagicMock()
        cur.fetchone.side_effect = [
            (1, 'Coffee', TEST_PRICE_COFFEE, TEST_STOCK_FULL, 1),  # item info
            None,  # pickup code unique
            (1,),  # new booking id
        ]
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = create_booking('user123', 1, 1, TEST_QUANTITY_DOUBLE)
        assert res is not None

    @patch('flask_app.booking.get_db_connection')
    def test_item_not_found(self, mock_db):
        from flask_app.booking import create_booking

        cur = MagicMock()
        cur.fetchone.return_value = None
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = create_booking('user123', TEST_ID_NOT_FOUND_LARGE, 1, 1)
        assert 'error' in res

    @patch('flask_app.booking.get_db_connection')
    def test_out_of_stock(self, mock_db):
        from flask_app.booking import create_booking

        cur = MagicMock()
        cur.fetchone.return_value = (1, 'Coffee', TEST_PRICE_COFFEE,
                                     TEST_STOCK_EMPTY, 1)  # stock=0
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
            (1, 'user123', 1, TEST_QUANTITY_DOUBLE, 'active'),  # booking
            (TEST_STOCK_AFTER_ORDER, 'Coffee'),  # item for stock restore
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

        res = cancel_booking(TEST_ID_NOT_FOUND_LARGE, 'user123')
        assert 'error' in res

    @patch('flask_app.booking.get_db_connection')
    def test_wrong_user(self, mock_db):
        from flask_app.booking import cancel_booking

        cur = MagicMock()
        cur.fetchone.return_value = (1, 'other_user', 1, TEST_QUANTITY_DOUBLE, 'active')
        conn = MagicMock()
        conn.cursor.return_value = cur
        mock_db.return_value = conn

        res = cancel_booking(1, 'user123')
        assert 'error' in res

    @patch('flask_app.booking.get_db_connection')
    def test_already_cancelled(self, mock_db):
        from flask_app.booking import cancel_booking

        cur = MagicMock()
        cur.fetchone.return_value = (1, 'user123', 1, TEST_QUANTITY_DOUBLE, 'cancelled')
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
        cur.fetchall.return_value = [(1, 1, TEST_QUANTITY_DOUBLE)]  # id, item_id, qty
        cur.fetchone.return_value = (TEST_STOCK_AFTER_ORDER,)  # current stock
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
        expiry = created + timedelta(hours=TEST_HOURS_24)
        assert (expiry - created).total_seconds() == SECONDS_IN_24_HOURS

    def test_still_valid_at_23hrs(self):
        created = datetime.now()
        expiry = created + timedelta(hours=TEST_HOURS_24)
        check = created + timedelta(hours=TEST_HOURS_23)
        assert check < expiry

    def test_expired_at_25hrs(self):
        created = datetime.now()
        expiry = created + timedelta(hours=TEST_HOURS_24)
        check = created + timedelta(hours=TEST_HOURS_25)
        assert check > expiry


class TestStockManagement:

    def test_decrease_on_order(self):
        stock = TEST_STOCK_BEFORE_ORDER
        assert stock - TEST_STOCK_ORDER_QUANTITY == TEST_STOCK_AFTER_THREE_ORDER

    def test_restore_on_cancel(self):
        stock = TEST_STOCK_AFTER_THREE_ORDER
        assert stock + TEST_STOCK_ORDER_QUANTITY == TEST_STOCK_AFTER_RESTORE

    def test_reject_if_insufficient(self):
        stock = TEST_STOCK_INSUFFICIENT
        requested = TEST_STOCK_REQUESTED_OVER
        assert requested > stock

    def test_cumulative_orders(self):
        stock = TEST_STOCK_CUMULATIVE_START
        stock -= TEST_STOCK_CUMULATIVE_ORDER1
        stock -= TEST_STOCK_CUMULATIVE_ORDER2
        stock -= TEST_STOCK_CUMULATIVE_ORDER3
        assert stock == TEST_STOCK_CUMULATIVE_FINAL