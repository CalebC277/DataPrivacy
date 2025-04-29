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

    Map.save("Map.html")
    webbrowser.open('file://' + os.path.realpath("Map.html"))

    with open("POIS.txt", "w", encoding="utf-8") as file:
        file.write("Points of Interest within the radius:\n\n")
        for poi in pois:
            file.write(f"{poi}\n")

    with open("chosen_poi.txt", "w", encoding="utf-8") as file:
        sorted_pois = sorted(poi_counter.items(), key=lambda x: x[1], reverse=True)
        for poi, count in sorted_pois:
            file.write(f"{poi} -> chosen {count} times\n")

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
    #for x in range(1000):
    for x in range(num_runs):
        chosen = random.choice(pois)
        poi_counter[chosen] += 1

    CreateMap(coords[0], coords[1], radius, pois, poi_counter, noise)

if __name__ == "__main__":
    Main()
