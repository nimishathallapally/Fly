from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["flight_booking"]

# Drop old collections if rerunning
for name in db.list_collection_names():
    db[name].drop()

# ===== 1. Airports (real data) =====
airport_data = [
    ("Indira Gandhi Intl", "Delhi"),
    ("Chhatrapati Shivaji", "Mumbai"),
    ("Kempegowda Intl", "Bengaluru"),
    ("Rajiv Gandhi Intl", "Hyderabad"),
    ("Netaji Subhas Chandra", "Kolkata"),
    ("Chennai Intl", "Chennai"),
    ("Sardar Vallabhbhai Patel", "Ahmedabad"),
    ("Pune Airport", "Pune"),
    ("Goa Intl", "Goa"),
    ("Jaipur Intl", "Jaipur"),
    ("Cochin Intl", "Kochi"),
    ("Lucknow Airport", "Lucknow"),
    ("Trivandrum Intl", "Thiruvananthapuram"),
    ("Bagdogra Airport", "Siliguri"),
    ("Visakhapatnam Airport", "Visakhapatnam"),
    ("Biju Patnaik Intl", "Bhubaneswar"),
    ("Dehradun Airport", "Dehradun"),
    ("Raipur Airport", "Raipur"),
    ("Varanasi Airport", "Varanasi"),
    ("Amritsar Airport", "Amritsar")
]

airports = []
for i, (airport_name, city) in enumerate(airport_data):
    airports.append({
        "_id": f"APT{i+1:02}",
        "name": airport_name,
        "city": city,
        "country": "India"
    })
db.airports.insert_many(airports)

# ===== 2. Travel Classes =====
travel_classes = [
    {"_id": "ECO", "name": "Economy", "capacity": 150},
    {"_id": "BUS", "name": "Business", "capacity": 50},
    {"_id": "FST", "name": "First", "capacity": 20}
]
db.travel_classes.insert_many(travel_classes)

# ===== 3. Flight Services =====
flight_services = []
for i in range(5):
    flight_services.append({
        "_id": f"SVC{i+1}",
        "name": f"Service {i+1}"
    })
db.flight_services.insert_many(flight_services)

# ===== 4. Flights =====
flights = []
for i in range(20):
    src = airports[i % 20]["_id"]
    dst = airports[(i+1) % 20]["_id"]
    dep_time = datetime(2025, 4, 15, 6 + i % 12)
    arr_time = dep_time + timedelta(hours=2)
    flights.append({
        "_id": f"FL{i+1:03}",
        "source_airport": src,
        "destination_airport": dst,
        "departure_time": dep_time,
        "arrival_time": arr_time,
        "airplane_type": "Airbus A320",
        "seat_details": [
            {
                "seat_id": f"FL{i+1:03}_ECO",
                "travel_class_id": "ECO",
                "flight_cost": [
                    {
                        "valid_from": "2025-04-01",
                        "valid_to": "2025-04-30",
                        "cost": random.randint(3000, 6000)
                    }
                ]
            },
            {
                "seat_id": f"FL{i+1:03}_BUS",
                "travel_class_id": "BUS",
                "flight_cost": [
                    {
                        "valid_from": "2025-04-01",
                        "valid_to": "2025-04-30",
                        "cost": random.randint(7000, 10000)
                    }
                ]
            }
        ]
    })
db.flights.insert_many(flights)

# ===== 5. Service Offerings =====
offerings = []
for i in range(20):
    offerings.append({
        "travel_class_id": random.choice(["ECO", "BUS", "FST"]),
        "service_id": f"SVC{random.randint(1, 5)}",
        "offered_yn": True,
        "from_date": "2025-01-01",
        "to_date": "2025-12-31"
    })
db.service_offerings.insert_many(offerings)

# ===== 6. Passengers =====
passengers = []
for i in range(20):
    passengers.append({
        "_id": f"P{i+1:03}",
        "first_name": f"First{i+1}",
        "last_name": f"Last{i+1}",
        "email": f"user{i+1}@email.com",
        "phone": f"98765432{i:02}",
        "address": f"{i+1} Sample St",
        "city": airport_data[i % len(airport_data)][1],
        "state": "State",
        "zipcode": f"1100{i+1:02}",
        "country": "India"
    })
db.passengers.insert_many(passengers)

# ===== 7. Reservations =====
reservations = []
for i in range(20):
    flight_id = f"FL{(i % 20) + 1:03}"
    reservations.append({
        "_id": f"R{i+1:03}",
        "passenger_id": f"P{i+1:03}",
        "seat_id": f"{flight_id}_ECO",
        "flight_id": flight_id,
        "date_of_reservation": datetime(2025, 4, 10 + (i % 5))
    })
db.reservations.insert_many(reservations)

# ===== 8. Payments =====
payments = []
for i in range(20):
    payments.append({
        "_id": f"PAY{i+1:03}",
        "reservation_id": f"R{i+1:03}",
        "status": random.choice(["Paid", "Pending"]),
        "due_date": datetime(2025, 4, 15),
        "amount": random.randint(3000, 10000)
    })
db.payments.insert_many(payments)

print("✅ Inserted 20+ entries into all collections with real airport and city names.")
