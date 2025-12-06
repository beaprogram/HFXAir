# Test-Driven Development (TDD) Documentation

## 1. Test Coverage 

### Overall Coverage Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Total Line Coverage** | **80%** | >75% |  Achieved |
| **Total Tests** | 160 | - | All Passed|
| **Tests Passing** | 160/160 (100%) | - | Passed|

### Module-wise Coverage Breakdown

| Module | Statements | Missed | Coverage | Description |
|--------|------------|--------|----------|-------------|
| `auth.py` | 21 | 1 | **95%** | Authentication & JWT handling |
| `shop.py` | 436 | 74 | **83%** | Shop listings, catalog, items |
| `booking.py` | 265 | 84 | **68%** | Reservations, cancellations |
| `app.py` | 181 | 86 | **52%** | Main Flask routes |
| `helper/helper_cron_jobs.py` | 129 | 105 | 19% | Background jobs (external) |
| `helper/helper_firebase_notification.py` | 130 | 119 | 8% | Push notifications (external) |


### Test Files Coverage

| Test File | Statements | Coverage |
|-----------|------------|----------|
| `tests/conftest.py` | 12 | 100% |
| `tests/test_arrivals_departures.py` | 18 | 100% |
| `tests/test_bookings.py` | 141 | 100% |
| `tests/test_flight_details.py` | 10 | 100% |
| `tests/test_flights.py` | 9 | 100% |
| `tests/test_integration.py` | 458 | 100% |
| `tests/test_login.py` | 57 | 96% |
| `tests/test_shopping_component.py` | 191 | 100% |
| `tests/test_shops.py` | 419 | 100% |
| `tests/test_subscribe.py` | 19 | 100% |

---

## 2. Border Conditions & Edge Cases

Our test suite comprehensively covers boundary conditions, null handling, and edge cases.

### 2.1 Boundary Value Testing

#### Stock Availability Thresholds

```python
# Testing exact boundary values for stock status
def test_get_availability_status_in_stock(self):
    """Stock > 5 should be in_stock"""
    assert get_availability_status(10) == 'in_stock'
    assert get_availability_status(6) == 'in_stock'   # Just above threshold

def test_get_availability_status_low_stock(self):
    """Stock 1-5 should be low_stock"""
    assert get_availability_status(5) == 'low_stock'  # Exact boundary
    assert get_availability_status(1) == 'low_stock'  # Lower boundary

def test_get_availability_status_out_of_stock(self):
    """Stock 0 or negative should be out_of_stock"""
    assert get_availability_status(0) == 'out_of_stock'   # Zero boundary
    assert get_availability_status(-1) == 'out_of_stock'  # Negative edge case
```

#### Quantity Validation

```python
def test_create_booking_invalid_quantity(self, client, monkeypatch):
    """POST /bookings with quantity > 3 returns 400"""
    # Tests maximum quantity boundary (max = 3)
    response = client.post("/bookings", json={
        "user_id": 1, "item_id": 1, "shop_id": 1, "quantity": 5
    })
    assert response.status_code == 400
    assert response.json["error"] == "Invalid quantity"
```

### 2.2 Null/Empty Input Handling

```python
def test_calculate_total_price_base_only(self):
    """Calculate price without variants (None)"""
    total = calculate_total_price(100.00, 2, None)
    assert total == 200.00

def test_calculate_total_price_empty_variants(self):
    """Calculate price with empty variants list"""
    total = calculate_total_price(50.00, 3, [])
    assert total == 150.00
```

### 2.3 Invalid Input Testing

```python
def test_get_bookings_invalid_user_id(self, client):
    """GET /bookings with invalid user_id returns 400"""
    response = client.get("/bookings?user_id=abc")  # String instead of int
    assert response.status_code == 400
    assert response.json["error"] == "Invalid user_id"

def test_create_booking_item_not_found(self, client, monkeypatch):
    """POST /bookings with invalid item_id returns 404"""
    response = client.post("/bookings", json={
        "user_id": 1, "item_id": 9999, "shop_id": 1, "quantity": 1
    })
    assert response.status_code == 404
```

### 2.4 State Edge Cases

```python
def test_cancel_booking_already_cancelled(self, client, monkeypatch):
    """POST /bookings/<id>/cancel for cancelled booking returns 400"""
    # Attempting to cancel an already cancelled reservation
    response = client.post("/bookings/1/cancel", json={"user_id": 1})
    assert response.status_code == 400
    assert response.json["error"] == "Already cancelled"

def test_create_booking_already_reserved(self, client, monkeypatch):
    """POST /bookings for already reserved item returns 400"""
    # Duplicate reservation prevention
    response = client.post("/bookings", json={...})
    assert response.json["error"] == "Already reserved"
```

### 2.5 Authorization Edge Cases

```python
def test_cancel_booking_forbidden(self, client, monkeypatch):
    """POST /bookings/<id>/cancel by different user returns 403"""
    # User trying to cancel another user's booking
    response = client.post("/bookings/1/cancel", json={"user_id": 2})
    assert response.status_code == 403
```

### Border Conditions Summary Table

| Test Category | Conditions Tested | Test Count |
|---------------|-------------------|------------|
| Boundary Values | Stock thresholds (0, 1, 5, 6), Quantity limits | 8 |
| Null/Empty Handling | None variants, Empty lists, Missing fields | 6 |
| Invalid Inputs | Wrong types, Non-existent IDs, Invalid formats | 7 |
| State Edge Cases | Already cancelled, Already reserved, Expired | 5 |
| Authorization | Wrong user, Missing auth, Invalid tokens | 4 |
| Database Errors | Connection failures, Query errors | 6 |

---

## 3. Integration Tests

### Overview

We have a dedicated `test_integration.py` file containing **50 integration tests** that verify the interaction between multiple system components.

### Integration Test Classes

| Test Class | Tests | Components Integrated |
|------------|-------|----------------------|
| `TestGetShops` | 10 | Shop module ↔ Database ↔ Time handling |
| `TestGetShopById` | 3 | Shop module ↔ Database |
| `TestShopHours` | 2 | Shop module ↔ Database ↔ Weekly schedules |
| `TestShopCategories` | 2 | Shop module ↔ Database aggregation |
| `TestShopCatalog` | 2 | Shop module ↔ Database ↔ Categories ↔ Items |
| `TestShopItems` | 4 | Shop module ↔ Database ↔ Variants ↔ Search |
| `TestItemById` | 3 | Shop module ↔ Database ↔ Variants |
| `TestItemCategories` | 2 | Shop module ↔ Database |
| `TestPickupCodes` | 4 | Booking module ↔ Database uniqueness check |
| `TestGetBookings` | 2 | Booking module ↔ Database ↔ User filtering |
| `TestCreateBooking` | 3 | Booking ↔ Item validation ↔ Stock ↔ Database |
| `TestCancelBooking` | 4 | Booking ↔ Auth ↔ Stock restoration ↔ Database |
| `TestExpireBookings` | 2 | Booking ↔ Cron logic ↔ Stock ↔ Database |
| `TestReservationExpiry` | 3 | Business rules ↔ Time calculations |
| `TestStockManagement` | 4 | Business rules ↔ Inventory operations |

### Key Integration Flows Tested

#### Flow 1: Shop Discovery → Item Browsing → Booking
```
get_shops() → get_shop_by_id() → get_shop_items() → create_booking()
     ↓              ↓                  ↓                  ↓
  Database      Database          Database +        Database +
  filtering     lookup            variants          stock update
```

#### Flow 2: Booking Lifecycle
```
create_booking() → get_user_bookings() → cancel_booking()
       ↓                   ↓                    ↓
  Stock decrease      Status filter       Stock restore +
  + Pickup code       + Item details      Status update
```

#### Flow 3: Booking Expiration (Background Job)
```
expire_old_bookings()
       ↓
  Find expired → Update status → Restore stock
```

### Integration Test Examples

```python
class TestCreateBooking:
    @patch('flask_app.booking.get_db_connection')
    def test_success(self, mock_db):
        """Tests: Item lookup → Stock check → Booking creation → Stock update"""
        cur = MagicMock()
        cur.fetchone.side_effect = [
            (1, 'Coffee', 2.99, 50, 1),  # Item validation
            None,                         # Pickup code uniqueness
            (1,),                         # New booking ID
        ]
        # ... verifies full integration flow
        
class TestCancelBooking:
    @patch('flask_app.booking.get_db_connection')
    def test_success(self, mock_db):
        """Tests: Booking lookup → Auth check → Cancel → Stock restore"""
        cur.fetchone.side_effect = [
            (1, 'user123', 1, 2, 'active'),  # Booking validation
            (48, 'Coffee'),                   # Item for stock restore
        ]
        # ... verifies cancel + stock restoration
```

---

## 4. Test Best Practices

### 4.1 Test Organization

| Practice | Implementation |
|----------|----------------|
| **Grouped by Feature** | Tests organized in classes (`TestGetShops`, `TestCreateBooking`) |
| **Descriptive Names** | `test_create_booking_out_of_stock`, `test_cancel_booking_forbidden` |
| **Single Responsibility** | Each test verifies one specific behavior |
| **Shared Fixtures** | Common setup in `conftest.py` |

### 4.2 Test Isolation

```python
# conftest.py - Shared test fixtures
@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

# Tests use mocking to isolate from external dependencies
@patch('flask_app.shop.get_db_connection')
def test_basic_listing(self, mock_db):
    # Database is mocked - test runs in isolation
```

### 4.3 No Test Smells

| Smell | Status | Evidence |
|-------|--------|----------|
| Duplicate Tests | None | Same method names exist in different classes (valid namespacing) |
| Flaky Tests |  None | 160/160 tests pass consistently |
| Test Interdependence |  None | Each test sets up its own mocks |
| Magic Numbers |  Avoided | Constants like `stock=50`, `quantity=2` have clear context |
| Assertion Roulette |  None | Each test has focused assertions with clear failure messages |

### 4.4 Mocking Strategy

```python
# External dependencies are properly mocked
@patch('flask_app.booking.get_db_connection')
def test_item_not_found(self, mock_db):
    cur = MagicMock()
    cur.fetchone.return_value = None  # Simulate not found
    conn = MagicMock()
    conn.cursor.return_value = cur
    mock_db.return_value = conn
    
    res = create_booking('user123', 9999, 1, 1)
    assert 'error' in res
```

---

## 5. TDD Adherence

### Red-Green-Refactor Evidence from Git History

Our commit history demonstrates consistent TDD practice with clear Red → Green → Refactor cycles.

### Feature: User Login

| Phase | Commit | Message | Date |
|-------|--------|---------|------|
| 🔴 Red | `18c6eddc` | Feature login Test case red | 2025-11-05 |
| 🟢 Green | `ffee9543` | Feature - login Test case green hardcoded route | 2025-11-05 |
| 🟢 Green | `ae6915e7` | Feature - login returns token Test red | 2025-11-06 |
| 🟢 Green | `36ea55ca` | Feature - login returns 400 for empty values Test red | 2025-11-06 |

### Feature: Flight Information

| Phase | Commit | Message | Date |
|-------|--------|---------|------|
| 🔴 Red | `e82033b1` | Feature - get flight list Test(with mock db) red | 2025-11-06 |
| 🔴 Red | `1d76cb40` | Feature - get flight details Test(with mock db) red | 2025-11-06 |
| 🟢 Green | `f611b328` | Feature - get flight details Test(with mock db) green bare minimum | 2025-11-06 |

### Feature: Flight Subscription

| Phase | Commit | Message | Date |
|-------|--------|---------|------|
| 🔴 Red | `7361812f` | Feature - user subscribes to a flight Test red | 2025-11-06 |
| 🟢 Green | `2d9a3c2d` | Feature - user subscribes to a flight Test green bare minimum | 2025-11-06 |
| 🔵 Refactor | `a658ddd6` | Feature - user subscribes to a flight Test green refractor with query insert | 2025-11-06 |

### Feature: Shop Endpoints

| Phase | Commit | Message | Date |
|-------|--------|---------|------|
| 🔴 Red | `d6003212` | test cases for shops endpoints Red | 2025-11-22 |
| 🟢 Green | `5cc4ba93` | bare minimum functions for shops endpoints green | 2025-11-22 |
| 🔵 Refactor | `ad7064c4` | refractor -updated complete test cases for shops endpoints | 2025-11-22 |

### Feature: Booking Module

| Phase | Commit | Message | Date |
|-------|--------|---------|------|
| 🟢 TDD | `b2108b62` | Add booking module - APIs for reserve, cancel, and view reservations (TDD) | 2025-12-03 |

### Feature: Shopping Component

| Phase | Commit | Message | Date |
|-------|--------|---------|------|
| 🟢 Green | `10d92bdd` | Add tests for shopping component: images, variants, timezone, time parsing | 2025-12-04 |
| 🟢 Green | `12284097` | Test coverage increased from 59% to 81% | 2025-12-04 |
| 🔵 Refactor | `6b4e2852` | removing magic numbers from all possible files | 2025-12-05 |
| 🔵 Refactor | `f398f006` | refactor: eliminate magic numbers and fix code smells from DPy analysis | 2025-12-05 |

### TDD Compliance Summary

| Metric | Value |
|--------|-------|
| Features developed with TDD | 6+ major features |
| Red-Green cycles documented | 8 clear cycles |
| Refactoring commits | 4 dedicated refactor commits |
| Coverage improvement commits | 59% → 81% → 83% |


---

## Appendix: Running Tests

### Run All Tests with Coverage
```bash
cd flask_app
source venv/bin/activate
pytest --cov=. --cov-report=term-missing tests/
```

### Generate HTML Coverage Report
```bash
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html
```

### Run Specific Test File
```bash
pytest tests/test_integration.py -v
```

### Run Tests by Class
```bash
pytest tests/test_bookings.py::TestCreateBookingAPI -v
```
