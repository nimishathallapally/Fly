# Fly – HCI Case Study

**Fly** is a Human-Computer Interaction (HCI) case study that explores the usability and design of **loading bars** and **CAPTCHAs** in web applications. This project simulates a flight booking system that includes booking forms, payment flow, and dynamic CAPTCHA selection — all styled using Tailwind CSS and built with Flask.

---

## Objectives

* Study user interaction with different types of captchas
* Evaluate the effectiveness of **loading indicators** in various parts of the user journey (e.g., during payments or data submission).
* Apply and demonstrate HCI principles such as:

  * Nielsen’s Heuristics
  * Shneiderman’s Golden Rules
  * Gestalt Laws of Perception
* Develop a visually appealing and responsive user interface using **Tailwind CSS**

---

## Features

* **Sign In / Sign Up** with form validation

* **Flight Booking Form** to capture journey details

* **Payment Page** with dynamic CAPTCHA selection

* **Various types of captchas

* **Loading Bars** to simulate data processing delays

* **Success & Feedback Pages**

* Fully styled with **Tailwind CSS**

---

## 📁 Project Structure

```
app/
│
├── static/
│   ├── captchas/                   # CAPTCHA generation logic
│   └── css/
│       ├── main.css                # Compiled Tailwind output
│       ├── style.css               # Custom styles
│       └── styles.css              # Tailwind base styles
│
├── templates/
│   ├── components/
│   │   ├── base.html
│   │   ├── header.html
│   │   └── footer.html
│   ├── index.html
│   ├── signin.html
│   ├── signup.html
│   ├── booking_details.html
│   ├── flights.html
│   ├── card_payment.html
│   ├── payment.html
│   ├── payment_success.html
│
├── db.py                # Initializes database
├── run.py               # Flask app entry point
├── tailwind.config.js   # Tailwind CSS configuration
├── package.json         # Tailwind build script and dependency
├── package-lock.json
└── README.md
```

---

## Requirements

* Python 3.8+
* Node.js (for Tailwind CSS)
* Flask (install via pip)
* Tailwind CSS (installed via npm)
* MongoDB (local or cloud instance)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/nimishathallapally/Fly.git
cd Fly
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install flask
pip install flask pymongo
```

### 3. Initialize the Database

```bash
python db.py
```

### 4. Start MongoDB

If you are using a local instance of MongoDB, make sure it is running:

```bash
sudo systemctl start mongod
```

To check if MongoDB is running, you can use:

```bash
sudo systemctl status mongod
```

### 5. Install Node.js Dependencies

```bash
npm install
```

### 6. Compile Tailwind CSS

```bash
npm run css
```

> This watches `styles.css` and compiles to `main.css` in the correct location.

### 7. Start the Flask App

```bash
python run.py
```

### 8. Access the Web App

Open your browser and navigate to:

```
http://localhost:5000
```

---

## License

This project is licensed under the MIT License.

---

## Notes

* You can modify the CAPTCHA difficulty and styling.
* The loading bar behavior can be tweaked using JavaScript and Tailwind transitions in relevant templates.

---

Thank you for exploring Commercia – an HCI-driven design prototype!

---
