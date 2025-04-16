from flask import Flask, render_template, request, redirect, url_for,session,flash,send_file
from pymongo import MongoClient
from datetime import datetime
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import string
from captcha.image import ImageCaptcha
from captcha.audio import AudioCaptcha
from gtts import gTTS
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64

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

@app.route('/audio-captcha')
def audio_captcha():
    audio = AudioCaptcha()
    captcha_text = '5g9x'  # Normally, you'd generate this randomly and store it in the session
    data = audio.generate(captcha_text)
    return send_file(data, mimetype='audio/wav')

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
@app.route('/card_payment', methods=['GET', 'POST'])
def card_payment():
    if request.method == 'POST':
        captcha_type = request.form.get('captcha_type', 'gimpy')

        if captcha_type == 'gimpy':
            user_input = request.form.get('captcha_response', '').strip().lower()
            expected = session.get('gimpy_captcha_answer', '').lower()
            if user_input != expected:
                return render_template('card_payment.html',
                                       captcha_image=session.get('captcha_image'),
                                       math_question=session.get('math_question'),
                                       error="Incorrect image CAPTCHA")

        elif captcha_type == 'math':
            user_input = request.form.get('captcha_response_math', '').strip()
            expected = session.get('math_captcha_answer', '')
            if user_input != expected:
                return render_template('card_payment.html',
                                       captcha_image=session.get('captcha_image'),
                                       math_question=session.get('math_question'),
                                       error="Incorrect math CAPTCHA")

        return render_template("payment_success.html")

    # === GET request: Generate CAPTCHA ===

    # Ensure CAPTCHA folder exists
    captcha_dir = os.path.join(app.static_folder, 'captcha')
    os.makedirs(captcha_dir, exist_ok=True)

    # Generate image CAPTCHA
    gimpy_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session['gimpy_captcha_answer'] = gimpy_text

    image_captcha = ImageCaptcha()
    image = image_captcha.generate_image(gimpy_text)

    image_filename = f"{gimpy_text}.png"
    image_path = os.path.join(captcha_dir, image_filename)
    image.save(image_path)

    # Store relative path for template
    session['captcha_image'] = f"captcha/{image_filename}"

    # Generate math CAPTCHA
    a, b = random.randint(1, 10), random.randint(1, 10)
    math_question = f"{a} + {b}"
    session['math_question'] = math_question
    session['math_captcha_answer'] = str(a + b)

    return render_template('card_payment.html',
                           captcha_image=session.get('captcha_image'),
                           math_question=math_question)


@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user_captcha = request.form.get('captcha', '').lower()
        session_captcha = session.get('captcha_text', '').lower()

        print(f"Username: {username}, Password: {password}, User CAPTCHA: {user_captcha}, Session CAPTCHA: {session_captcha}")

        if user_captcha != session_captcha:
            flash('Incorrect CAPTCHA. Please try again.', 'error')
            return redirect(url_for('signin'))

        flash('Signed in successfully!', 'success')
        return redirect('/')

    # --- GET request: generate new CAPTCHA ---
    captcha_text = ''.join(random.choices(string.digits, k=5))
    session['captcha_text'] = captcha_text
    print(f"Generated CAPTCHA: {captcha_text}")

    spoken_text = ' '.join(captcha_text)  # E.g., "5 2 3 9 1"
    audio_dir = os.path.join(app.static_folder, 'audio')
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    audio_file = os.path.join(audio_dir, f'{captcha_text}.mp3')
    if not os.path.exists(audio_file):
        try:
            tts = gTTS(text=spoken_text, lang='en', slow=False)
            tts.save(audio_file)
            print(f"Generated CAPTCHA audio: {audio_file}")
        except Exception as e:
            print(f"Error generating audio for CAPTCHA: {e}")

    return render_template('signin.html', captcha_audio=f'/static/audio/{captcha_text}.mp3')

RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        recaptcha_response = request.form.get('g-recaptcha-response')

        # Validate reCAPTCHA
        recaptcha_verification = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
        )
        result = recaptcha_verification.json()
        if not result.get('success'):
            return render_template('signup.html', error="reCAPTCHA verification failed. Please try again.")

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")

        # Store user in DB (replace with actual MongoDB insertion)
        # db.users.insert_one({"name": name, "email": email, "password": password})

        return redirect(url_for('index'))

    return render_template('signup.html')



@app.route('/generate_captcha')
def generate_captcha():
    # Generate random string
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session['captcha'] = captcha_text

    # Create image
    img = Image.new('RGB', (150, 50), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 32)
    draw.text((10, 5), captcha_text, font=font, fill=(0, 0, 0))

    # Save to buffer
    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
