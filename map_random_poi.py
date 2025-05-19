import folium
from geopy.geocoders import Nominatim
from folium import Circle
import webbrowser
import os
import requests
import re
import random
from collections import defaultdict
import warnings
import numpy as np
import matplotlib.pyplot as plt

OVERPASS_URL = "http://overpass-api.de/api/interpreter"
os.environ["OMP_NUM_THREADS"] = "1"
warnings.filterwarnings(
    "ignore",
    message="Could not find the number of physical cores*",
    category=UserWarning
)

def GetCoordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def FindPOIs(lat, lon, rad):
    query = f"""
    [out:json];
    (
      node["amenity"](around:{rad * 1000},{lat},{lon});
      node["tourism"](around:{rad * 1000},{lat},{lon});
      node["leisure"](around:{rad * 1000},{lat},{lon});
      node["shop"](around:{rad * 1000},{lat},{lon});

      way["amenity"](around:{rad * 1000},{lat},{lon});
      way["tourism"](around:{rad * 1000},{lat},{lon});
      way["leisure"](around:{rad * 1000},{lat},{lon});
      way["shop"](around:{rad * 1000},{lat},{lon});

      relation["amenity"](around:{rad * 1000},{lat},{lon});
      relation["tourism"](around:{rad * 1000},{lat},{lon});
      relation["leisure"](around:{rad * 1000},{lat},{lon});
      relation["shop"](around:{rad * 1000},{lat},{lon});
    );
    out center tags;
    """
    response = requests.get(OVERPASS_URL, params={'data': query})
    data = response.json()
    pois = []
    for el in data['elements']:
        name = el.get('tags', {}).get('name', 'Unnamed POI')
        lat = el.get('lat')
        lon = el.get('lon')

        if lat is None or lon is None:
            center = el.get('center')
            if center:
                lat = center.get('lat')
                lon = center.get('lon')

        if lat is not None and lon is not None and name != 'Unnamed POI':
            category = ', '.join([f"{k}={v}" for k, v in el.get('tags', {}).items() if k != 'name'])
            pois.append(f"{name} at ({lat}, {lon}) [{category}]")

    return pois

def ParsePOI(poi):
    try:
        name_match = re.match(r"^(.*?) at", poi)
        coords_match = re.search(r"\(([-\d.]+), ([-\d.]+)\)", poi)

        if name_match and coords_match:
            name = name_match.group(1).strip()
            lat = coords_match.group(1)
            lon = coords_match.group(2)
            return name, lat, lon
        else:
            raise ValueError("No match found")
    except Exception as e:
        print("Failed to parse:", poi)
        return "Unknown", "0", "0"

def CreateMap(lat, lon, rad, pois, poi_counter, noise):
    Map = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup="Selected Location").add_to(Map)

    Circle(
        location=(lat, lon),
        radius=rad * 1000,
        color='blue',
        fill=True,
        fill_opacity=0.3
    ).add_to(Map)

    offset_points = []
    for poi in pois:
        name, latStr, lonStr = ParsePOI(poi)
        latF = float(latStr)
        lonF = float(lonStr)

        # folium.Marker(
        #     location=[latF, lonF],
        #     popup=f"{name} (chosen {poi_counter[poi]}x)",
        #     icon=folium.Icon(color='green', icon='ok-sign')
        # ).add_to(Map)

        #NOISE = 0.002
        for x in range(poi_counter[poi]):
            offset_lat = latF + random.uniform(-noise, noise)
            offset_lon = lonF + random.uniform(-noise, noise)
            folium.CircleMarker(
                location=[offset_lat, offset_lon],
                radius=2,
                color='black',
                fill=True,
                fill_opacity=1
            ).add_to(Map)
            offset_points.append((offset_lat, offset_lon))               

    Map.save("Map.html")
    webbrowser.open('file://' + os.path.realpath("Map.html"))

    with open("random_poi.txt", "w", encoding="utf-8") as file:
        file.write("Random POI's with noise: (lat, lon): \n")
        for offset_lat, offset_lon in offset_points:
            file.write(f"({offset_lat}, {offset_lon})\n")

    with open("chosen_poi.txt", "w", encoding="utf-8") as file:
        sorted_pois = sorted(poi_counter.items(), key=lambda x: x[1], reverse=True)
        for poi, count in sorted_pois:
            if count > 0:
                name, lat_str, lon_str = ParsePOI(poi)
                file.write(f"{name} ({lat_str}, {lon_str})\n")

def CalculateDistance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance    

def Main():
    ch = input("Type 'Address' or 'Coordinates': ").strip().lower()

    if ch == 'address':
        address = input("Enter address: ")
        coords = GetCoordinates(address)
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
        noise = float(input("Enter amount of noise (KM): "))
    except ValueError:
        print("Invalid Noise Value")
        return
    
    try:
        num_runs = int(input("Enter number of runs: "))
    except ValueError:
        print("Invalid number of runs")
        return

    pois = FindPOIs(coords[0], coords[1], radius)
    if not pois:
        print("No POIs found.")
        return

    poi_counter = defaultdict(int)
    utility_values = []
    privacy_values = []

    for x in range(num_runs):
        chosen = random.choice(pois)
        poi_counter[chosen] += 1

        utility = 0.0
        privacy = 0.0

        for poi, count in poi_counter.items():
            name, latStr, lonStr = ParsePOI(poi)
            latF = float(latStr)
            lonF = float(lonStr)
            dist = CalculateDistance(coords[0], coords[1], latF, lonF)
            utility += dist / len(poi_counter)
        
        centroid_lat = sum(float(ParsePOI(poi)[1]) for poi in poi_counter) / len(poi_counter)
        centroid_lon = sum(float(ParsePOI(poi)[2]) for poi in poi_counter) / len(poi_counter)
        privacy = CalculateDistance(coords[0], coords[1], centroid_lat, centroid_lon)

        utility_values.append(utility)
        privacy_values.append(privacy)

        print(f"Iteration {x + 1}")
        print(f"Privacy = {privacy}")
        print(f"Utility = {utility}")
        print("")



    CreateMap(coords[0], coords[1], radius, pois, poi_counter, noise)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(range(1, num_runs + 1), utility_values, marker='o', color='green')
    plt.title('Utility vs Iteration')
    plt.xlabel('Iteration')
    plt.ylabel('Utility (Avg Distance to Chosen POIs)')

    plt.subplot(1, 2, 2)
    plt.plot(range(1, num_runs + 1), privacy_values, marker='o', color='red')
    plt.title('Privacy vs Iteration')
    plt.xlabel('Iteration')
    plt.ylabel('Privacy (Distance to Centroid of POIs)')

    plt.tight_layout()
    plt.savefig("POI_Utility_Privacy_Graph")
    plt.show()

if __name__ == "__main__":
    Main()
