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

# Detailed planet data to display on the planets page
PLANETS = [
    {
        "name": "Mercury",
        "emoji": "☿️",
        "radius_km": 2439.7,
        "mass_10^24kg": 0.330,
        "distance_mkm": 57.9,
        "gravity_m_s2": 3.7,
        "orbital_period_days": 88,
        "moons": 0,
        "atmosphere": "Trace (exosphere): O, Na, H, He",
        "surface_temp_c": "-173 to 427",
        "composition": "Rocky",
        "fun_fact": "Smallest planet and fastest orbit around the Sun."
    },
    {
        "name": "Venus",
        "emoji": "♀️",
        "radius_km": 6051.8,
        "mass_10^24kg": 4.87,
        "distance_mkm": 108.2,
        "gravity_m_s2": 8.87,
        "orbital_period_days": 225,
        "moons": 0,
        "atmosphere": "CO2 (96%), N2 (3%), clouds of H2SO4",
        "surface_temp_c": "~462",
        "composition": "Rocky with dense CO2 atmosphere",
        "fun_fact": "Surface pressure ~92× Earth; hottest planet due to runaway greenhouse effect."
    },
    {
        "name": "Earth",
        "emoji": "🌍",
        "radius_km": 6371.0,
        "mass_10^24kg": 5.97,
        "distance_mkm": 149.6,
        "gravity_m_s2": 9.807,
        "orbital_period_days": 365.25,
        "moons": 1,
        "atmosphere": "N2 (78%), O2 (21%), trace gases",
        "surface_temp_c": "-88 to 58",
        "composition": "Rocky; water-rich",
        "fun_fact": "Only known planet with stable liquid water on the surface."
    },
    {
        "name": "Mars",
        "emoji": "♂️",
        "radius_km": 3389.5,
        "mass_10^24kg": 0.642,
        "distance_mkm": 227.9,
        "gravity_m_s2": 3.71,
        "orbital_period_days": 687,
        "moons": 2,
        "atmosphere": "CO2 (~95%), N2, Ar",
        "surface_temp_c": "-125 to 20",
        "composition": "Rocky; iron-oxide gives red color",
        "fun_fact": "Home to the tallest volcano in the Solar System (Olympus Mons)."
    },
    {
        "name": "Jupiter",
        "emoji": "♃",
        "radius_km": 69911,
        "mass_10^24kg": 1898,
        "distance_mkm": 778.6,
        "gravity_m_s2": 24.79,
        "orbital_period_days": 4333,
        "moons": 79,
        "atmosphere": "H2, He; bands of clouds (NH3, H2O)",
        "surface_temp_c": "~-145 (cloud tops)",
        "composition": "Gas giant (H/He)",
        "fun_fact": "Largest planet; Great Red Spot is a long-lived storm."
    },
    {
        "name": "Saturn",
        "emoji": "♄",
        "radius_km": 58232,
        "mass_10^24kg": 568,
        "distance_mkm": 1433.5,
        "gravity_m_s2": 10.44,
        "orbital_period_days": 10759,
        "moons": 83,
        "atmosphere": "H2, He; prominent ring system",
        "surface_temp_c": "~-178 (cloud tops)",
        "composition": "Gas giant with extensive rings",
        "fun_fact": "Least dense planet; would float in a large enough ocean."
    },
    {
        "name": "Uranus",
        "emoji": "♅",
        "radius_km": 25362,
        "mass_10^24kg": 86.8,
        "distance_mkm": 2872.5,
        "gravity_m_s2": 8.69,
        "orbital_period_days": 30687,
        "moons": 27,
        "atmosphere": "H2, He, CH4 (gives blue color)",
        "surface_temp_c": "~-216",
        "composition": "Ice giant (ices and gases)",
        "fun_fact": "Rotates on its side; extreme seasons."
    },
    {
        "name": "Neptune",
        "emoji": "♆",
        "radius_km": 24622,
        "mass_10^24kg": 102,
        "distance_mkm": 4495.1,
        "gravity_m_s2": 11.15,
        "orbital_period_days": 60190,
        "moons": 14,
        "atmosphere": "H2, He, CH4",
        "surface_temp_c": "~-214",
        "composition": "Ice giant",
        "fun_fact": "Strongest sustained winds measured in the Solar System."
    }
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
    # Compute planet orbital speeds (approximate mean orbital speed)
    planet_speeds = []
    import math
    for p in PLANETS:
        # distance_mkm is million km from sun (approx semi-major axis)
        dist_km = float(p.get('distance_mkm', 0)) * 1e6
        period_days = float(p.get('orbital_period_days', 1))
        period_seconds = period_days * 86400.0 if period_days else 1.0
        circumference_km = 2.0 * math.pi * dist_km
        speed_km_s = circumference_km / period_seconds
        planet_speeds.append({
            'name': p['name'],
            'emoji': p.get('emoji',''),
            'speed_km_s': round(speed_km_s, 3),
            'speed_km_h': round(speed_km_s * 3600.0, 1),
            'orbital_period_days': p.get('orbital_period_days')
        })

    # Compute asteroid speed statistics from latest data
    asteroid_vels = [a.get('velocity', 0) for a in LATEST_DATA.get('asteroids', []) if a.get('velocity') is not None]
    asteroid_stats = {}
    if asteroid_vels:
        asteroid_stats['count'] = len(asteroid_vels)
        asteroid_stats['avg_km_s'] = round(sum(asteroid_vels) / len(asteroid_vels), 3)
        asteroid_stats['min_km_s'] = round(min(asteroid_vels), 3)
        asteroid_stats['max_km_s'] = round(max(asteroid_vels), 3)
        asteroid_stats['top_5'] = sorted([{'name': a.get('name',''), 'velocity': a.get('velocity',0)} for a in LATEST_DATA.get('asteroids', [])], key=lambda x: x['velocity'], reverse=True)[:5]
    else:
        asteroid_stats = {'count': 0, 'avg_km_s': 0, 'min_km_s': 0, 'max_km_s': 0, 'top_5': []}

    return render_template(
        "index.html",
        asteroids=LATEST_DATA["asteroids"],
        updated=LATEST_DATA["last_updated"],
        planets=PLANETS,
        planet_speeds=planet_speeds,
        asteroid_stats=asteroid_stats
    )


@app.route('/planets')
def planets_page():
    return render_template(
        'planets.html',
        planets=PLANETS,
        updated=LATEST_DATA["last_updated"]
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
