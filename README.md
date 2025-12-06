<<<<<<< HEAD
# HFXAIR - Halifax Stanfield International Airport App

A mobile application for travelers at Halifax Stanfield International Airport (YHZ) providing real-time flight information, airport shop directory, and item reservation system.

---
## Features Description

Click on [Features](Documentation/USER_STORIES.md) to view the explanation of features implemented in the application.

## Technology Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | React Native 0.82.1, TypeScript, React 19.1.1 |
| Backend | Python Flask, Flask-SQLAlchemy |
| Database | MariaDB (db-5308.cs.dal.ca) |
| Authentication | JWT (PyJWT) |
| Push Notifications | Firebase Cloud Messaging |
| Background Jobs | APScheduler |

---

## Dependencies

### Frontend Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | 19.1.1 | React library |
| react-native | 0.82.1 | Mobile framework |
| @react-navigation/native | ^7.1.19 | Navigation framework |
| @react-navigation/stack | ^7.6.3 | Stack navigation |
| @react-native-firebase/app | ^23.5.0 | Firebase core SDK |
| @react-native-firebase/messaging | ^23.5.0 | Push notifications |
| axios | ^1.12.2 | HTTP client |
| react-native-gesture-handler | ^2.20.2 | Gesture handling |
| react-native-safe-area-context | ^5.6.2 | Safe area handling |
| react-native-screens | ^4.18.0 | Native screen components |
| react-native-vector-icons | ^10.2.0 | Icon library |

#### Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| typescript | ^5.8.3 | TypeScript compiler |
| @babel/core | ^7.25.2 | Babel compiler |
| jest | ^29.6.3 | Testing framework |
| eslint | ^8.19.0 | Code linting |
| prettier | 2.8.8 | Code formatting |

### Backend Dependencies

| Package | Purpose |
|---------|---------|
| flask | Web framework for REST API |
| flask_sqlalchemy | SQLAlchemy integration |
| PyMySQL | MySQL/MariaDB database driver |
| python-dotenv | Environment variable management |
| pyjwt | JWT token encoding/decoding |
| firebase-admin | Firebase Admin SDK for push notifications |
| pytz | Timezone handling (America/Halifax) |
| APScheduler | Background job scheduling |
| pytest | Testing framework |
| pytest-flask | Flask testing utilities |
| pytest-cov | Test coverage reporting |

---

## Build and Deployment Instructions

### Prerequisites

- Node.js >= 20
- Python 3.8+
- Android Studio (for Android development, make an android simulator)
- Firebase project with Cloud Messaging enabled

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API base URL:**
   
   Edit `src/services/axiosProvider.ts` and update the `baseURL`:
   ```typescript
   const axiosInstance: AxiosInstance = axios.create({
     baseURL: 'http://172.17.1.217',
     timeout: 10000,
     headers: {
       'Content-Type': 'application/json',
     },
   });
   ```

4. **Add Firebase configuration:**
   
   Place `google-services.json` in `frontend/android/app/`

5. **Start Metro bundler:**
   ```bash
   npm start
   ```

6. **Run on Android (in a new terminal):**
   ```bash
   npx react-native run-android
   ```

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd flask_app
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   
   On Linux/Mac:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` file:**
   
   Create a `.env` file in `flask_app/` with the following configuration:
   ```env
   FLASK_ENV=production
   
   DATABASE_URL=jdbc:mariadb://db-5308.cs.dal.ca:3306/CSCI5308_1_DEVINT
   DB_HOST=db-5308.cs.dal.ca
   DB_NAME=CSCI5308_1_DEVINT
   DB_USER=CSCI5308_1_DEVINT_USER
   DB_PASSWORD=<your_password>
   
   AIRPORT_NAME=Halifax (YHZ)
   ```

6. **Add Firebase service account key:**
   
   Place your Firebase service account JSON file in the `flask_app/` directory.

7. **Run the server:**
   ```bash
   flask run --host=0.0.0.0
   ```
   
   Or for production:
   ```bash
   python app.py
   ```

### Verifying Database Connection

Run the database connection test:
```bash
cd flask_app
python test_db_connection.py
```

Expected output:
```
✓ Connected successfully!
✓ MariaDB/MySQL version: X.X.X
✓ Flights table exists with X rows
✓ Database connection test passed!
```

---

## DEPLOYMENT INSTRUCTIONS

Click on [Deployment](Documentation/Deployment.md) to check the complete deployment instructions along with major issues and its solution.

## Project Structure

```
group01/
├── frontend/                 # React Native mobile app
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── screens/          # Screen components
│   │   │   ├── auth/         # Login, Loading, GuestFlight
│   │   │   ├── shops/        # Shop views and catalog
│   │   │   └── tabs/         # Main tab screens
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API communication (Axios)
│   │   ├── navigation/       # Navigation configuration
│   │   ├── types/            # TypeScript definitions
│   │   └── utils/            # Helper functions
│   ├── android/              # Android native code
│   └── package.json          # Frontend dependencies
│
├── flask_app/                # Flask REST API backend
│   ├── app.py                # Main application
│   ├── auth.py               # JWT authentication
│   ├── shop.py               # Shop endpoints
│   ├── booking.py            # Booking endpoints
│   ├── helper/               # Firebase & cron helpers
│   ├── tests/                # Pytest test suite
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment configuration
│
└── README.md                 # This file
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Authenticate with flight_number and ticket_number |

### Flights

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/flights` | Get all flights |
| GET | `/flights/<flight_id>` | Get flight details |
| GET | `/flights/arrivals` | Get arriving flights |
| GET | `/flights/departures` | Get departing flights |

### Shops

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/shops` | List all shops |
| GET | `/shops/<shop_id>` | Get shop details |
| GET | `/shops/<shop_id>/hours` | Get shop hours |
| GET | `/shops/<shop_id>/items` | Get shop items |
| GET | `/shops/categories` | Get shop categories |

### Bookings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/bookings` | Get user's bookings |
| POST | `/bookings` | Create reservation |
| POST | `/bookings/<id>/cancel` | Cancel reservation |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/send-notification` | Send push notification |
| POST | `/subscribe` | Subscribe to flight updates |

---

## Usage Scenarios

Click on [Usage](Documentation/Usage_Scenarios.md) to find all the usage scenarios of all the features implemented in the applicaton.

---

## CI/CD Pipeline
We followed **Build** ----> **Test**(80% Code Coverage) -----> **Deploy** ----> **Code quality** with four stages for CI/CD pipeline development.

Click on [CI/CD](Documentation/CICD_PIPELINE_SETUP.md) to know about the complete CI/CD Pipeline setup for the application along with proper explanation with commans and some issues and its solution.

---

## TDD (Test-Driven Development)

Click on [TDD](Documentation/TDD_Documentation.md) to see the complete documentation on TDD.

---

## Design Principles

Click on [Design](Documentation/Design_Principles.md) to know about the implementation of design principles in the development part of the application.

## Code Quality Analysis

Click on [Code-Quality](Documentation/REFACTORING_DOCUMENTATION.md) to find the refactoring documentation and also gives explanation of smells identified and refactored.


## Code Quality Reports

Go to **Documentation/Code_Quality_Files(Before Refactoring)** for code quality reports before refactoring.

Go to **Documentation/Code_Quality_Files(After Refactoring)** for code quality reports after refactoring.

## Other Clean Code Practices

Click on [Other_Clean_Code_Practices](Documentation/Clean_Code_Documentation.md) for information about clean code practices followed in the main files of the backend part.


=======
>>>>>>> 458c8ee8 (-testing ci/cd)
