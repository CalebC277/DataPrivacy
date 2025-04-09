import folium
from geopy.geocoders import Nominatim
from folium import Circle
import webbrowser
import os
import requests

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

def GetCoordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None
    
def FindRestaurants(lat, lon, rad):
    query = f"""
    [out:json];
    (
      node["amenity"="restaurant"](around:{rad * 1000},{lat},{lon});
      way["amenity"="restaurant"](around:{rad * 1000},{lat},{lon});
      relation["amenity"="restaurant"](around:{rad * 1000},{lat},{lon});
    );
    out body;
    """

    response = requests.get(OVERPASS_URL, params={'data': query})
    data = response.json()

    restaurants = []
    for el in data['elements']:
        name = el.get('tags', {}).get('name', 'Unnamed restaurant')
        lat = el.get('lat', 0)
        lon = el.get('lon', 0)
        address = f"{name} at ({lat}, {lon})"
        restaurants.append(address)
    
    return restaurants

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
    data = response.json();
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


def CreateMap(lat, lon, rad, restaurants, pois):
    Map = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup="Selected Location").add_to(Map)

    Circle(
        location = (lat, lon),
        radius = rad * 1000,
        color = 'blue',
        fill = True,
        fill_opacity = 0.3
    ).add_to(Map)

    Map.save("Map.html")

    webbrowser.open('file://' + os.path.realpath("Map.html"))

    with open("Restaurants.txt", "w", encoding="utf-8") as file:
        file.write("Restaurants within the radius:\n\n")
        for r in restaurants:
            file.write(f"{r}\n")

    with open("POIS.txt", "w", encoding="utf-8") as file:
        file.write("Points of Interest within the radius:\n\n")
        for poi in pois:
            file.write(f"{poi}\n")

def Main():
    #print("Address or Coordinates?")
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
    
    restaurants = FindRestaurants(coords[0], coords[1], radius)
    #restaurants = []

    pois = FindPOIs(coords[0], coords[1], radius)

    CreateMap(coords[0], coords[1], radius, restaurants, pois)

if __name__ == "__main__":
    Main()