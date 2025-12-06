# HFXAIR - User Stories Documentation

## User Stories Summary

| Issue # | User Story | Weight | 
|---------|------------|--------|
| #3 | Passenger Login and Guest Login | 5 | 
| #4 | Home - Quick Access to Key Pages | 5 | 
| #5 | Arrival Feature Page | 3 |   
| #6 | Departure Feature Page | 3 |     
| #7 | HFX Airport Map | 3 |
| #8 | Browse Shops with Hours | 5 | 
| #9 | About Feature Page | 1 | 
| #10 | Push Notifications | 8 | 
| #11 | View a Shop's Catalog | 5 |
| #12 | Book an Item for 24 Hours | 5 | 
| #13 | Move Booked Item Back to Catalog (Release) | 3 | 
| | **TOTAL** | **46** | |

---

## Detailed User Stories

### #3 - Passenger Login and Guest Login
**Weight:** 5 Story Points

**Description:**  
As a user, I want to be able to log in as a passenger using my flight number and ticket number, or continue as a guest, so that I can access the airport services.

**Acceptance Criteria:**
- User can log in with valid flight number and ticket number
- User can continue as guest without credentials
- Invalid credentials show appropriate error message
- Successful login redirects to home page

---

### #4 - Home - Quick Access to Key Pages
**Weight:** 5 Story Points

**Description:**  
As a user, I want a home page with quick access tiles to key features, so that I can easily navigate to the most important sections of the app.

**Acceptance Criteria:**
- Home page displays quick access tiles
- Tiles link to Arrivals, Departures, Shops, Map, etc.
- Layout is intuitive and user-friendly

---

### #5 - Arrival Feature Page
**Weight:** 3 Story Points

**Description:**  
As a user, I want to view arriving flights at Halifax Stanfield Airport, so that I can track incoming flights.

**Acceptance Criteria:**
- Display list of arriving flights
- Show flight number, origin, scheduled time, and status
- Real-time status updates

---

### #6 - Departure Feature Page
**Weight:** 3 Story Points

**Description:**  
As a user, I want to view departing flights from Halifax Stanfield Airport, so that I can track outgoing flights.

**Acceptance Criteria:**
- Display list of departing flights
- Show flight number, destination, scheduled time, and status
- Real-time status updates

---

### #7 - HFX Airport Map
**Weight:** 3 Story Points

**Description:**  
As a user, I want to view a map of Halifax Stanfield Airport, so that I can navigate the terminal easily.

**Acceptance Criteria:**
- Display airport terminal map
- Map is zoomable and readable
- Key locations are marked

---

### #8 - Browse Shops with Hours
**Weight:** 5 Story Points

**Description:**  
As a user, I want to browse all shops at the airport with their operating hours, so that I can plan my shopping.

**Acceptance Criteria:**
- Display list of all airport shops
- Show shop name, location, and operating hours
- Shops are categorized appropriately

---

### #9 - About Feature Page
**Weight:** 1 Story Point

**Description:**  
As a user, I want to view information about the HFXAIR app and Halifax Stanfield Airport, so that I can learn more about the services offered.

**Acceptance Criteria:**
- Display app information
- Show airport details and contact information

---

### #10 - Push Notifications
**Weight:** 8 Story Points

**Description:**  
As a user, I want to receive push notifications about my flight status, so that I am always informed about changes to my flight.

**Acceptance Criteria:**
- User receives notifications for flight status changes
- Notifications work when app is in background
- User can enable/disable notifications
- Notifications are timely and accurate

---

### #11 - View a Shop's Catalog
**Weight:** 5 Story Points

**Description:**  
As a user, I want to view a shop's catalog of items, so that I can see what products are available for purchase.

**Acceptance Criteria:**
- Display list of items for selected shop
- Show item name, description, and availability
- Items are displayed with images if available

---

### #12 - Book an Item for 24 Hours
**Weight:** 5 Story Points

**Description:**  
As a user, I want to book/reserve an item from a shop for 24 hours, so that I can pick it up later at my convenience.

**Acceptance Criteria:**
- User can select an item and book it
- Booking is valid for 24 hours
- Confirmation is shown after successful booking
- Item is marked as reserved in the catalog

---

### #13 - Move Booked Item Back to Catalog (Release)
**Weight:** 3 Story Points

**Description:**  
As a user, I want to release/cancel my booking and move the item back to the catalog, so that I can free up items I no longer need.

**Acceptance Criteria:**
- User can view their booked items
- User can release/cancel a booking
- Released item returns to available catalog
- Confirmation is shown after successful release

---

## Story Points Distribution

```
Push Notifications (#10)     ████████ 8 pts (17.4%)
Passenger Login (#3)         █████ 5 pts (10.9%)
Home Quick Access (#4)       █████ 5 pts (10.9%)
Browse Shops (#8)            █████ 5 pts (10.9%)
View Catalog (#11)           █████ 5 pts (10.9%)
Book Item (#12)              █████ 5 pts (10.9%)
Arrivals (#5)                ███ 3 pts (6.5%)
Departures (#6)              ███ 3 pts (6.5%)
Airport Map (#7)             ███ 3 pts (6.5%)
Release Booking (#13)        ███ 3 pts (6.5%)
About Page (#9)              █ 1 pt (2.2%)
                             ─────────────────
TOTAL                        46 Story Points
```

---

## Team Contributions

| Team Member | Tasks Completed |
|-------------|-----------------|
| Arup Halder | 14 |
| Dhrumil Gajjar | 10 |
| Jashwanth Pantra Chittibabu | 13 |
| Harsh Pandey | 13 |
| Devanshu Mundhiyara | 25 |
| **TOTAL** | **64** |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React Native, TypeScript |
| Backend | Flask, Python |
| Database | MariaDB |
| Notifications | Firebase Cloud Messaging |
| Version Control | GitLab |


