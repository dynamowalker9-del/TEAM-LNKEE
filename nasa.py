import requests 

NASA_API_KEY = 'h8c4eFLjGwQ0D6L9fdPN95mckzEBpYppGBAd9B5Z'
NEO_URL = 'https://api.nasa.gov/neo/rest/v1/feed'

FIREBALL_URL = "https://ssd-api.jpl.nasa.gov/fireball.api"

def get_asteroid(start_date,end_date):
    params={
        "start_date": start_date,
        "end_date": end_date,
        "api_key": NASA_API_KEY
    }

    try:
        response = requests.get(NEO_URL, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"API request failed: {e}")
        return []
    
    # Check for API error response
    if "error" in data:
        print(f"API error: {data['error'].get('message', 'Unknown error')}")
        return []
    
    if "near_earth_objects" not in data:
        print(f"Unexpected API response: {data}")
        return []
    
    asteroids = []

    for date in data["near_earth_objects"]:
        for neo in data["near_earth_objects"][date]:
            asteroids.append({
                "id": neo.get("id") or neo.get("neo_reference_id"),
                "name": neo["name"],
                "diameter": round(
                    neo["estimated_diameter"]["meters"]["estimated_diameter_max"], 2
                ),
                "velocity":round(
                    float(neo["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"]), 2
                ),
                "distance":round(
                    float(neo["close_approach_data"][0]["miss_distance"]["kilometers"]),0
                ),
                "hazardous": neo["is_potentially_hazardous_asteroid"]  
            })
    return asteroids 
       
def get_fireballs(limits=10):
    try:
        response = requests.get(FIREBALL_URL, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Fireball API request failed: {e}")
        return []
    
    if "error" in data:
        return []

    events = []
    for row in data["data"][:limits]:
        events.append({
            "date": row[0],
            "energy": row[1],
            "lat": row[3],
            "lon": row[4]

        })
    return events


def get_neo_details(neo_id):
    lookup = f'https://api.nasa.gov/neo/rest/v1/neo/{neo_id}'
    try:
        resp = requests.get(lookup, params={"api_key": NASA_API_KEY}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if "error" in data:
            return None
    except Exception as e:
        print(f"NEO detail fetch failed: {e}")
        return None

    details = {
        "id": data.get("id"),
        "name": data.get("name"),
        "absolute_magnitude_h": data.get("absolute_magnitude_h"),
        "nasa_jpl_url": data.get("nasa_jpl_url"),
        "is_potentially_hazardous_asteroid": data.get("is_potentially_hazardous_asteroid"),
        "first_observation_date": data.get("orbital_data", {}).get("first_observation_date"),
        "last_observation_date": data.get("orbital_data", {}).get("last_observation_date"),
        "orbit_class": data.get("orbital_data", {}).get("orbit_class", {}).get("orbit_class_type")
    }
    return details


def is_threat(distance_km, velocity_kms):
    return distance_km < 7500000 and velocity_kms > 20

