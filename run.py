from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'app/templates'), static_folder=os.path.join(os.path.dirname(__file__), 'app/static'))

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["flight_booking"]

@app.route('/')
def index():
    airports = list(db.airports.find())
    return render_template("index.html", airports=airports)
@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/search_flights', methods=["POST"])
def search_flights():
    source = request.form["source"]
    destination = request.form["destination"]
    travel_date = request.form["date"]
    travel_class = request.form["class"]

    # Parse date
    try:
        travel_date_obj = datetime.strptime(travel_date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format"

    # Filter flights
    flights = list(db.flights.find({
        "source_airport": source,
        "destination_airport": destination
    }))

    # Filter seat details for selected class
    for flight in flights:
        seat_info = next((s for s in flight["seat_details"] if s["travel_class_id"] == travel_class), None)
        flight["selected_seat"] = seat_info

    return render_template("flights.html", flights=flights, travel_class=travel_class, date=travel_date_obj)

if __name__ == '__main__':
    app.run(debug=True)
