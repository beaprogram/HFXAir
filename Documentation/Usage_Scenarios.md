### Scenario 1: User Authentication

**Actor:** Traveler with a flight booking

**Flow:**
1. User opens the HFXAIR app
2. User enters their flight number (e.g., `AC301`)
3. User enters their ticket number (e.g., `TCK456`)
4. System validates credentials against the database
5. On success, system returns a JWT token (valid for 24 hours)
6. User is redirected to the Home Screen

**API Used:** `POST /login`

### Scenario 2: User without Valid Flight Tickets( Guest Login)

**Actor** Traveller/Customer without a valid flight booking

**Flow:**
1. User opens the HFXAIR app
2. If user doesnt have any valid flight details
3. User can click on guest login button
4. Upon clicking on guest login button, user can access to limited functionality of the app (i.e. Only Arrivals and departure details)

### Scenario 3: Viewing Flight Arrivals

**Actor:** Any user (authenticated or guest)

**Flow:**
1. User navigates to the "Arrivals" tab
2. System fetches all flights where destination = "Halifax (YHZ)"
3. User sees a list of arriving flights with:
   - Flight number and airline
   - Origin city
   - Scheduled and actual arrival times
   - Status (On Time, Delayed, Landed)
   - Gate and terminal information
   - Baggage claim belt number

**API Used:** `GET /flights/arrivals`

### Scenario 4: Viewing Flight Departures

**Actor:** Any user (authenticated or guest)

**Flow:**
1. User navigates to the "Departures" tab
2. System fetches all flights where origin = "Halifax (YHZ)"
3. User sees a list of departing flights with:
   - Flight number and airline
   - Destination city
   - Scheduled and actual departure times
   - Status (On Time, Delayed, Boarding, Departed)
   - Gate and terminal information
   - Boarding time

**API Used:** `GET /flights/departures`

### Scenario 5: Subscribing to Flight Notifications

**Actor:** Authenticated user

**Flow:**
1. User views their flight details
2. User taps "Enable Notifications" button
3. System registers the user's device token with the flight
4. When flight status changes, system sends push notification
5. User receives real-time updates on their device

**API Used:** `POST /subscribe`, `POST /send-notification`

### Scenario 6: Browsing Airport Shops

**Actor:** Authenticated User

**Flow:**
1. User navigates to the "Shops" tab
2. User sees a list of all airport shops with:
   - Shop name and category
   - Current open/closed status
   - Terminal and gate location
3. User can filter by category (Food, Retail, Services)
4. User can filter by "Open Now" to see currently open shops
5. User taps a shop to view details including weekly hours

**API Used:** `GET /shops`, `GET /shops/<shop_id>`, `GET /shops/categories`

### Scenario 7: Viewing Shop Items and Catalog

**Actor:** Authenticated User

**Flow:**
1. User opens a shop's detail page
2. User taps "View Catalog" or "Browse Items"
3. System displays items organized by category
4. User can search items by name
5. User can filter by price range
6. User can filter by availability (in stock, low stock)
7. User taps an item to view details including variants and pricing

**API Used:** `GET /shops/<shop_id>/items`, `GET /shops/<shop_id>/catalog`, `GET /items/<item_id>`

### Scenario 8: Making a Reservation

**Actor:** Authenticated user

**Flow:**
1. User browses shop items and selects an item
2. User views item details (price, variants, availability)
3. User selects quantity (1-3) and any variants (size, color)
4. User taps "Reserve Item"
5. System validates stock availability
6. System creates booking with unique 6-character pickup code
7. User receives confirmation with pickup code
8. Reservation expires after 24 hours if not picked up

**API Used:** `POST /bookings`

### Scenario 9: Managing Reservations

**Actor:** Authenticated user

**Flow:**
1. User navigates to "My Reservations"
2. User sees all active, completed, and cancelled reservations
3. For active reservations, user can:
   - View pickup code
   - See expiration time
   - Cancel the reservation
4. When cancelled, stock is automatically restored

**API Used:** `GET /bookings`, `POST /bookings/<id>/cancel`