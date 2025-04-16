from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient
from datetime import datetime
import os
import random
import string
from captcha.image import ImageCaptcha

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "app/templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "app/static"),
)
app.secret_key = "12345"
# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["flight_booking"]

captcha_dir = os.path.join(app.static_folder, 'captchas')

# Create captcha directory if it doesn't exist
if not os.path.exists(captcha_dir):
    os.makedirs(captcha_dir)

def generate_captcha_text():
    # You can replace this with your own logic to generate captcha text
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


@app.route("/")
def index():
    airports = list(db.airports.find())
    return render_template("index.html", airports=airports)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/search_flights", methods=["POST"])
def handle_search_flights():
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
    flights = list(
        db.flights.find({"source_airport": source, "destination_airport": destination})
    )

    # Filter seat details for selected class
    for flight in flights:
        seat_info = next(
            (s for s in flight["seat_details"] if s["travel_class_id"] == travel_class),
            None,
        )
        flight["selected_seat"] = seat_info
        flight["_id"] = str(flight["_id"])  # Convert ObjectId to string

    return render_template(
        "flights.html", flights=flights, travel_class=travel_class, date=travel_date_obj
    )


@app.route("/search_flights", methods=["GET"])
def show_search_form():
    return redirect(
        url_for("index")
    )  # or render a dedicated search form if you have one


@app.route("/booking-details", methods=["GET", "POST"])
def booking_details():
    # Get the flight ID from the query string
    flight_id = request.args.get("flight_id")

    # Find the flight document using the custom String ID (not ObjectId)
    flight = db.flights.find_one({"_id": flight_id})

    if not flight:
        return "Flight not found", 404

    # If POST method is used, handle booking form submission
    if request.method == "POST":
        # Handle passenger booking details here
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")

        # Here, you can save the data (e.g., store it in a database)
        # For now, we just print the details
        print(f"Name: {name}, Email: {email}, Phone: {phone}, Address: {address}")

        # After submission, redirect to the payment page
        return redirect(url_for("payment"))

    return render_template("booking_details.html", flight=flight)


@app.route("/payment")
def payment():
    # Payment page route
    return render_template("payment.html")


@app.route('/card_payment', methods=['GET', 'POST'])
def card_payment():
    if request.method == 'POST':
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']
        captcha_response = request.form['captcha_response']

        # Check if the CAPTCHA response is correct
        if captcha_response != session.get('captcha_text'):
            return render_template('card_payment.html', error="Incorrect CAPTCHA, please try again.")

        # Process the payment (skip for demo)
        return redirect(url_for('payment_success'))

    # Generate CAPTCHA text and image
    captcha_text = generate_captcha_text()
    session['captcha_text'] = captcha_text

    image = ImageCaptcha()
    captcha_image_path = os.path.join(captcha_dir, f'{captcha_text}.png')

    # Write the CAPTCHA image to the file system
    image.write(captcha_text, captcha_image_path)

    # Render the template with the correct image path
    return render_template('card_payment.html', captcha_image=f'captchas/{captcha_text}.png')



if __name__ == "__main__":
    app.run(debug=True)
