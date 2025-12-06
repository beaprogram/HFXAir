### SOLID Principles Implementation

#### 1. Single Responsibility Principle (SRP)

Each module in the backend has a single, well-defined responsibility:

| Module | Responsibility |
|--------|----------------|
| `app.py` | Flight endpoints and application initialization |
| `auth.py` | Authentication middleware (JWT validation) |
| `shop.py` | Shop-related endpoints and business logic |
| `booking.py` | Booking/reservation management |
| `helper_firebase_notification.py` | Push notification delivery |
| `helper_cron_jobs.py` | Background job scheduling |

**Example from `auth.py`:**
```python
# auth.py has ONE responsibility: JWT authentication
def require_auth(secret_key):
    """Authentication middleware decorator."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Only handles token validation - nothing else
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing token"}), 401
            # ... validation logic
        return wrapper
    return decorator
```

#### 2. Open/Closed Principle (OCP)

The codebase is open for extension but closed for modification:

**Example:** The `require_auth` decorator can be applied to any new endpoint without modifying the decorator itself:
```python
# Adding new protected endpoint - no changes to auth.py needed
@app.get("/new-feature")
@require_auth(SECRET)
def new_feature():
    return jsonify({"data": "protected"})
```

**Example:** Shop filtering is extensible:
```python
# New filters can be added without modifying existing filter logic
def get_shops(category=None, open_now=None, sort=None, terminal=None, gate=None):
    # Each filter is independent - new filters can be added
```

#### 3. Liskov Substitution Principle (LSP)

Database functions return consistent data structures that can be used interchangeably:

```python
# All flight-related functions return the same structure
def get_all_flights(): ...      # Returns list of flight dicts
def get_arrivals(): ...         # Returns list of flight dicts  
def get_departures(): ...       # Returns list of flight dicts

# Any of these can be used wherever flight data is needed
```

#### 4. Interface Segregation Principle (ISP)

The API is divided into focused, specific endpoints rather than one large endpoint:

```
Instead of: GET /shops?include=hours,items,catalog,categories

We have:
  GET /shops                    → Basic shop list
  GET /shops/<id>              → Shop details
  GET /shops/<id>/hours        → Operating hours only
  GET /shops/<id>/items        → Items only
  GET /shops/<id>/catalog      → Catalog structure only
  GET /shops/categories        → Categories only
```

Clients only request what they need, reducing payload size and coupling.

#### 5. Dependency Inversion Principle (DIP)

High-level modules don't depend on low-level modules; both depend on abstractions:

**Example:** Database connection is abstracted:
```python
# High-level functions depend on get_db_connection(), not direct pymysql calls
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        # ... configuration from environment
    )

# Business logic uses the abstraction
def get_all_flights():
    conn = get_db_connection()  # Doesn't know about pymysql details
    # ... business logic
```

---

### Cohesion and Coupling Analysis

#### High Cohesion

Each module contains related functionality:

| Module | Cohesion Level | Reason |
|--------|----------------|--------|
| `auth.py` | **High** | Only contains authentication logic |
| `shop.py` | **High** | Only contains shop-related operations |
| `booking.py` | **High** | Only contains booking operations |
| `helper_firebase_notification.py` | **High** | Only handles push notifications |

#### Low Coupling

Modules interact through well-defined interfaces:

- `booking.py` imports only `app` and `get_db_connection` from `app.py`
- `shop.py` imports only `app` and `get_db_connection` from `app.py`
- Helper modules are imported at application startup, not within business logic

---

### LCOM (Lack of Cohesion of Methods) Analysis

LCOM measures how closely the methods of a class are related. Lower values indicate better cohesion.

#### Backend Analysis

Since Python modules are used rather than classes, we analyze module-level cohesion:

| Module | Functions | Shared Data | LCOM Score | Interpretation |
|--------|-----------|-------------|------------|----------------|
| `auth.py` | 1 | JWT secret | **0 (Best)** | Single function, perfect cohesion |
| `shop.py` | 10 | DB connection, timezone | **Low (~0.2)** | Functions share common dependencies |
| `booking.py` | 8 | DB connection | **Low (~0.2)** | Functions share common dependencies |
| `app.py` | 12 | DB connection, JWT secret | **Medium (~0.4)** | Mix of auth and flight logic |

**LCOM Calculation Method:**

For module-level analysis:
```
LCOM = 1 - (sum of shared variables per function pair) / (total possible pairs × total variables)
```

#### Frontend Analysis (React Components)

| Component | Props Used | State Variables | LCOM Score | Interpretation |
|-----------|------------|-----------------|------------|----------------|
| `FlightCard.tsx` | flight data | - | **0 (Best)** | Single responsibility |
| `NotificationCenter.tsx` | notifications | enabled state | **Low** | Related state and props |
| `ShopListView.tsx` | shops, filters | loading, error | **Low** | Cohesive shop display logic |

---

### Design Patterns Used

#### 1. Decorator Pattern

Used for authentication middleware:
```python
@require_auth(SECRET)
def protected_endpoint():
    ...
```

#### 2. Factory Pattern

Database connections are created through a factory function:
```python
def get_db_connection():
    return pymysql.connect(...)
```

#### 3. Repository Pattern

Database operations are encapsulated in dedicated functions:
```python
def get_user_bookings(user_id, status=None): ...
def create_booking(user_id, item_id, ...): ...
def cancel_booking(booking_id, user_id): ...
```

#### 4. Provider Pattern (Frontend)

Axios instance is provided as a configured singleton:
```typescript
// axiosProvider.ts
const axiosInstance: AxiosInstance = axios.create({
  baseURL: 'http://172.17.1.217',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;