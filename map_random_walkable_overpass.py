import folium
from geopy.geocoders import Nominatim
from folium import Circle
import webbrowser
import os
import requests
from tqdm import tqdm

# === CONFIG ===
OVERPASS_URL = "http://overpass-api.de/api/interpreter"

def get_coordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def FindWalkableAreas(lat, lon, rad):
    query = f"""
    [out:json];
    (
      way["highway"](around:{rad * 1000},{lat},{lon})
        ["highway"!~"motorway|motorway_link"];
    );
    out center tags;
    """
    try:
        response = requests.get(OVERPASS_URL, params={'data': query}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Overpass API error:", e)
        return []

    walkable_areas = []
    for el in data.get('elements', []):
        center = el.get('center')
        if center:
            lat_center = center.get('lat')
            lon_center = center.get('lon')
            if lat_center is not None and lon_center is not None:
                highway_type = el['tags'].get('highway', 'unknown')
                name = el['tags'].get('name', f"Walkable Area ({highway_type})")
                walkable_areas.append((name, lat_center, lon_center, f"highway={highway_type}", "walkable"))
    return walkable_areas

def create_map(center_lat, center_lon, radius_km, walkable_areas):
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    folium.Marker([center_lat, center_lon], popup="Center Location").add_to(Map)

    Circle(
        location=(center_lat, center_lon),
        radius=radius_km * 1000,
        color='blue',
        fill=True,
        fill_opacity=0.2
    ).add_to(Map)

    for name, lat, lon, tags, _ in walkable_areas:
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color='black',
            fill=True,
            fill_opacity=1,
            popup=f"{name}\n{tags}"
        ).add_to(Map)

    Map.save("WalkableMapOverpass.html")
    webbrowser.open('file://' + os.path.realpath("WalkableMapOverpass.html"))

def save_to_file(points, filename="walkable_overpass.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Walkable areas:\n\n")
        for name, lat, lon, tags, status in points:
            f.write(f"{name}: ({lat}, {lon}) [{tags}]\n")

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
        num_runs = int(input("Enter number of points to keep: "))
    except ValueError:
        print("Invalid number of points")
        return

    center_lat, center_lon = coords

    print("Finding walkable areas using Overpass API...")
    walkable_areas = FindWalkableAreas(center_lat, center_lon, radius)

    if not walkable_areas:
        print("No walkable areas found.")
        return

    walkable_areas = walkable_areas[:num_runs]
    print(f"Found {len(walkable_areas)} walkable areas.")

    save_to_file(walkable_areas)
    create_map(center_lat, center_lon, radius, walkable_areas)

if __name__ == "__main__":
    main()
