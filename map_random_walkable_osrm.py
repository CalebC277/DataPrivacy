import folium
from geopy.geocoders import Nominatim
from folium import Circle
import webbrowser
import os
import requests
import random
import math
from tqdm import tqdm

# === CONFIG ===
NUM_POINTS = 1000
OSRM_URL = "http://router.project-osrm.org/route/v1/foot"

def get_coordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def generate_random_point(lat, lon, radius_km):
    radius_deg = radius_km / 111
    angle = random.uniform(0, 2 * math.pi)
    r = radius_deg * math.sqrt(random.uniform(0, 1))
    dx = r * math.cos(angle)
    dy = r * math.sin(angle)
    return lat + dy, lon + dx

def is_walkable(lat1, lon1, lat2, lon2):
    url = f"{OSRM_URL}/{lon1},{lat1};{lon2},{lat2}?overview=false"
    try:
        response = requests.get(url)
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

    Map.save("WalkableMapOSRM.html")
    webbrowser.open('file://' + os.path.realpath("WalkableMapOSRM.html"))

def save_to_file(points, filename="walkable_osrm.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Walkable points (lat, lon):\n\n")
        for lat, lon in points:
            f.write(f"({lat}, {lon})\n")

def main():
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

    print("Generating walkable locations... (using OSRM)")
    for _ in tqdm(range(NUM_POINTS), desc="Checking walkability"):
        lat, lon = generate_random_point(center_lat, center_lon, radius)
        if is_walkable(center_lat, center_lon, lat, lon):
            walkable_points.append((lat, lon))

    print(f"Found {len(walkable_points)} walkable points.")
    save_to_file(walkable_points)
    create_map(center_lat, center_lon, radius, walkable_points)

if __name__ == "__main__":
    main()
