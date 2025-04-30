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
#NUM_POINTS = 1000
NUM_POINTS = 1
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

def is_routable(lat, lon):
    url = f"http://router.project-osrm.org/nearest/v1/foot/{lon},{lat}?number=1"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code != 200:
            return False
        data = response.json()
        return "waypoints" in data and len(data["waypoints"]) > 0
    except Exception as e:
        print("Nearest check error:", e)
        return False


# def is_walkable(lat1, lon1, lat2, lon2):
#     url = f"{OSRM_URL}/{lon1},{lat1};{lon2},{lat2}?overview=false"
#     print(url)
#     try:
#         response = requests.get(url)
#         data = response.json()
#         return "routes" in data and len(data["routes"]) > 0
#     except Exception as e:
#         print("Routing error:", e)
#         return False

def is_walkable(lat1, lon1, lat2, lon2):
    url = f"{OSRM_URL}/{lon1},{lat1};{lon2},{lat2}?overview=false"
    print(url)
    try:
        #response = requests.get(url, timeout=5)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Routing error: HTTP {response.status_code}")
            return False
        if not response.content.strip():
            print("Routing error: Empty response")
            return False
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
    
    try:
        num_runs = int(input("Enter number of runs: "))
    except ValueError:
        print("Invalid number of runs")
        return

    center_lat, center_lon = coords
    walkable_points = []

    print("Generating walkable locations... (using OSRM)")
    #for _ in tqdm(range(NUM_POINTS), desc="Checking walkability"):
    # for _ in tqdm(range(num_runs), desc="Checking walkability"):
    #     lat, lon = generate_random_point(center_lat, center_lon, radius)
    #     if is_routable(lat, lon) and is_walkable(center_lat, center_lon, lat, lon):
    #         walkable_points.append((lat, lon))

    with tqdm(total=num_runs, desc="Checking walkability") as pbar:
        while len(walkable_points) < num_runs:
            lat, lon = generate_random_point(center_lat, center_lon, radius)
            if is_routable(lat, lon) and is_walkable(center_lat, center_lon, lat, lon):
                walkable_points.append((lat, lon))
                pbar.update(1)


    print(f"Found {len(walkable_points)} walkable points.")
    save_to_file(walkable_points)
    create_map(center_lat, center_lon, radius, walkable_points)

if __name__ == "__main__":
    main()
