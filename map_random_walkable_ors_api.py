import folium
from geopy.geocoders import Nominatim
from folium import Circle
import webbrowser
import os
import requests
import random
import math
import time
from tqdm import tqdm  # NEW

# === CONFIG ===
NUM_POINTS = 1000
OVERPASS_URL = "http://overpass-api.de/api/interpreter"
os.environ["OMP_NUM_THREADS"] = "1"

def get_coordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def generate_random_point(lat, lon, radius_km):
    radius_deg = radius_km / 111  # Rough conversion from km to degrees
    angle = random.uniform(0, 2 * math.pi)
    r = radius_deg * math.sqrt(random.uniform(0, 1))
    dx = r * math.cos(angle)
    dy = r * math.sin(angle)
    return lat + dy, lon + dx

def is_walkable(lat1, lon1, lat2, lon2, api_key):
    url = f"https://api.openrouteservice.org/v2/directions/foot-walking"
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [[lon1, lat1], [lon2, lat2]]
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        data = response.json()
        return "routes" in data and len(data["routes"]) > 0
    except Exception as e:
        print("Routing error:", e)
        return False

def create_map(center_lat, center_lon, radius_km, walkable_points):
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    folium.Marker([center_lat, center_lon], popup="Center Location").add_to(Map)

    Circle(
        location=(center_lat, center_lon),
        radius=radius_km * 1000,
        color='blue',
        fill=True,
        fill_opacity=0.2
    ).add_to(Map)

    for lat, lon in walkable_points:
        folium.CircleMarker(
            location=[lat, lon],
            radius=2,
            color='black',
            fill=True,
            fill_opacity=1
        ).add_to(Map)

    Map.save("WalkableMapORS.html")
    webbrowser.open('file://' + os.path.realpath("WalkableMapORS.html"))

def save_to_file(points, filename="walkable_ors.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Walkable points (lat, lon):\n\n")
        for lat, lon in points:
            f.write(f"({lat}, {lon})\n")

def main():
    # api_key = input("Enter your OpenRouteService API Key: ").strip()
    api_key = os.getenv("ORS_API_KEY")
    if not api_key:
        raise ValueError("OpenRouteService API key not found. Set ORS_API_KEY environment variable.")

    ch = input("Type 'Address' or 'Coordinates': ").strip().lower()
    if ch == 'address':
        address = input("Enter address: ")
        coords = get_coordinates(address)
        if not coords:
            print("Address not found")
            return
    elif ch == 'coordinates':
        try:
            lat = float(input("Latitude: "))
            lon = float(input("Longitude: "))
            coords = (lat, lon)
        except ValueError:
            print("Invalid Coordinates")
            return
    else:
        print("Invalid Entry")
        return

    try:
        radius = float(input("Radius (KM): "))
    except ValueError:
        print("Invalid Radius")
        return

    center_lat, center_lon = coords
    walkable_points = []

    print("Generating walkable locations... (this might take a few minutes)")
    for _ in tqdm(range(NUM_POINTS), desc="Progress"):
        lat, lon = generate_random_point(center_lat, center_lon, radius)
        if is_walkable(center_lat, center_lon, lat, lon, api_key):
            walkable_points.append((lat, lon))
        time.sleep(0.1)  # Delay to avoid hitting API rate limits

    print(f"\nFound {len(walkable_points)} walkable points.")
    save_to_file(walkable_points)
    create_map(center_lat, center_lon, radius, walkable_points)

if __name__ == "__main__":
    main()

