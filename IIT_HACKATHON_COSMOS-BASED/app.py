from flask import Flask, render_template, jsonify, request
from datetime import date, timedelta
from nasa import get_asteroid, get_neo_details, get_fireballs
import threading
import time

app = Flask(__name__)

LATEST_DATA = {
    "asteroids": [],
    "last_updated": None
}

# Minimal planet data to display in the dashboard
PLANETS = [
    {"name": "Mercury", "emoji": "☿️", "radius_km": 2439.7, "mass_10^24kg": 0.330, "distance_mkm": 57.9, "desc": "Small, rocky, closest to Sun."},
    {"name": "Venus", "emoji": "♀️", "radius_km": 6051.8, "mass_10^24kg": 4.87, "distance_mkm": 108.2, "desc": "Thick atmosphere, very hot."},
    {"name": "Earth", "emoji": "🌍", "radius_km": 6371.0, "mass_10^24kg": 5.97, "distance_mkm": 149.6, "desc": "Our home planet."},
    {"name": "Mars", "emoji": "♂️", "radius_km": 3389.5, "mass_10^24kg": 0.642, "distance_mkm": 227.9, "desc": "Red planet with thin atmosphere."},
    {"name": "Jupiter", "emoji": "♃", "radius_km": 69911, "mass_10^24kg": 1898, "distance_mkm": 778.6, "desc": "Gas giant, largest planet."},
    {"name": "Saturn", "emoji": "♄", "radius_km": 58232, "mass_10^24kg": 568, "distance_mkm": 1433.5, "desc": "Gas giant with rings."},
    {"name": "Uranus", "emoji": "♅", "radius_km": 25362, "mass_10^24kg": 86.8, "distance_mkm": 2872.5, "desc": "Ice giant, tilted axis."},
    {"name": "Neptune", "emoji": "♆", "radius_km": 24622, "mass_10^24kg": 102, "distance_mkm": 4495.1, "desc": "Farthest known planet, windy."}
]

def fetch_and_store_neo_data():
    today = date.today()
    tomorrow = today + timedelta(days=1)

    asteroid = get_asteroid(
        today.isoformat(),
        tomorrow.isoformat()
    )

    # Use demo data if API fails (for testing)
    if not asteroid:
        asteroid = [
            {"id": "2000433", "name": "Eros (433)", "diameter": 8.4, "velocity": 18.5, "distance": 225000000, "hazardous": False},
            {"id": "2023001", "name": "Demo Asteroid A", "diameter": 150.0, "velocity": 22.3, "distance": 5000000, "hazardous": True},
            {"id": "2023002", "name": "Demo Asteroid B", "diameter": 45.5, "velocity": 19.2, "distance": 8500000, "hazardous": False},
        ]
        print("Using demo data (API unavailable)")

    LATEST_DATA["asteroids"] = asteroid
    LATEST_DATA["last_updated"] = time.strftime("%Y-%m-%d %H:%M UTC")

def refresh_neo_data():
    while True:
        fetch_and_store_neo_data()
        time.sleep(600)  # every 10 minutes

@app.route("/")
def index():
    return render_template(
        "index.html",
        asteroids=LATEST_DATA["asteroids"],
        updated=LATEST_DATA["last_updated"],
        planets=PLANETS
    )

@app.route('/neo/<neo_id>')
def neo_lookup(neo_id):
    details = get_neo_details(neo_id)
    if not details:
        return jsonify({"error": "not found"}), 404
    return jsonify(details)

@app.route('/fireballs')
def fireballs_route():
    events = get_fireballs(20)
    return jsonify(events)

if __name__ == "__main__":
    fetch_and_store_neo_data()  # initial load
    threading.Thread(target=refresh_neo_data, daemon=True).start()
    app.run(debug=True)
