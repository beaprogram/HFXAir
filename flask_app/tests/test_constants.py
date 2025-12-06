"""
Test Constants - Eliminates Magic Numbers in Test Files

This file contains all constants used throughout the test suite
to replace hardcoded "magic numbers" for better maintainability.

Usage:
    from flask_app.tests.test_constants import HTTP_OK, TEST_ITEM_PRICE
    assert response.status_code == HTTP_OK
"""

# =============================================================================
# HTTP Status Codes (for test assertions)
# =============================================================================

# Success codes (2xx)
HTTP_OK = 200
HTTP_CREATED = 201

# Client error codes (4xx)
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

# =============================================================================
# Test Data - Prices
# =============================================================================

# Common test prices
TEST_PRICE_COFFEE = 2.99
TEST_PRICE_PERFUME_BASE = 89.99
TEST_PRICE_PERFUME_SMALL = 44.99
TEST_PRICE_ADJUSTMENT_SMALL = -45.00
TEST_PRICE_ADJUSTMENT_LARGE = 85.00
TEST_PRICE_ADJUSTMENT_NONE = 0.00

# Booking test prices
TEST_BOOKING_TOTAL_BASIC = 165.00
TEST_BOOKING_TOTAL_DOUBLE = 330.00
TEST_BOOKING_TOTAL_TWO_COFFEES = 5.98

# Price filter test values
TEST_PRICE_MIN = 2.00
TEST_PRICE_MAX = 5.00

# =============================================================================
# Test Data - Quantities and Counts
# =============================================================================

# Stock quantities
TEST_STOCK_FULL = 50
TEST_STOCK_LOW = 10
TEST_STOCK_AFTER_ORDER = 48
TEST_STOCK_EMPTY = 0
TEST_STOCK_INITIAL = 20

# Order quantities
TEST_QUANTITY_SINGLE = 1
TEST_QUANTITY_DOUBLE = 2
TEST_QUANTITY_TRIPLE = 3
TEST_QUANTITY_INVALID = 5
TEST_QUANTITY_ORDER_LARGE = 7

# List/array counts
TEST_VARIANT_COUNT = 2
TEST_CATEGORY_COUNT = 3
TEST_SHOP_COUNT = 2

# Uniqueness test iterations
TEST_UNIQUENESS_ITERATIONS = 50
TEST_UNIQUENESS_MIN_UNIQUE = 45

# =============================================================================
# Test Data - IDs
# =============================================================================

# Valid test IDs
TEST_SHOP_ID = 1
TEST_SHOP_ID_ALT = 2
TEST_ITEM_ID = 1
TEST_ITEM_ID_PERFUME = 10
TEST_BOOKING_ID = 1
TEST_USER_ID = 1
TEST_USER_ID_ALT = 2
TEST_CATEGORY_ID = 1
TEST_FLIGHT_ID = 14

# Invalid/non-existent IDs
TEST_ID_NOT_FOUND = 999
TEST_ID_NOT_FOUND_LARGE = 9999

# =============================================================================
# Test Data - Time Constants
# =============================================================================

# Seconds in time periods
SECONDS_IN_24_HOURS = 86400

# Hours for testing
TEST_HOURS_23 = 23
TEST_HOURS_24 = 24
TEST_HOURS_25 = 25

# =============================================================================
# Test Data - Pickup Codes
# =============================================================================

# From main constants - pickup code specs
PICKUP_CODE_LENGTH = 6

# Test pickup codes
TEST_PICKUP_CODE = 'ABC123'
TEST_PICKUP_CODE_ALT = 'XYZ789'

# =============================================================================
# Test Data - Item Categories
# =============================================================================

TEST_CATEGORY_BEVERAGES_COUNT = 10
TEST_CATEGORY_FOOD_COUNT = 5
TEST_CATEGORY_DESSERTS_COUNT = 8

# Shop category counts (for /shops/categories endpoint)
TEST_SHOP_CAT_FOOD_BEV_COUNT = 15
TEST_SHOP_CAT_RETAIL_COUNT = 12
TEST_SHOP_CAT_SERVICES_COUNT = 8

# =============================================================================
# Test Data - Additional Prices
# =============================================================================

TEST_PRICE_ITEM_BASIC = 2.49
TEST_PRICE_ADJUST_SIZE = 1.00

# =============================================================================
# Test Data - Stock Management
# =============================================================================

# Stock operation test values
TEST_STOCK_BEFORE_ORDER = 10
TEST_STOCK_ORDER_QUANTITY = 3
TEST_STOCK_AFTER_THREE_ORDER = 7
TEST_STOCK_AFTER_RESTORE = 10
TEST_STOCK_INSUFFICIENT = 2
TEST_STOCK_REQUESTED_OVER = 5

# Cumulative order test values
TEST_STOCK_CUMULATIVE_START = 20
TEST_STOCK_CUMULATIVE_ORDER1 = 5
TEST_STOCK_CUMULATIVE_ORDER2 = 3
TEST_STOCK_CUMULATIVE_ORDER3 = 7
TEST_STOCK_CUMULATIVE_FINAL = 5

# =============================================================================
# Test Data - Shop Hours
# =============================================================================

TEST_OPEN_HOUR = 6
TEST_CLOSE_HOUR = 22
TEST_NOON_HOUR = 12
TEST_EARLY_HOUR = 5
TEST_LATE_HOUR = 23

# =============================================================================
# Test Data - Authentication
# =============================================================================

TEST_FLIGHT_NUMBER = "AC301"
TEST_FLIGHT_NUMBER_ALT = "AC123"
TEST_FLIGHT_NUMBER_INVALID = "WRONG"
TEST_TICKET_NUMBER = "TCK456"
TEST_TICKET_NUMBER_ALT = "TCK123"
TEST_TICKET_NUMBER_INVALID = "INVALID"