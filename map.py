import folium
from geopy.geocoders import Nominatim
from folium import Circle
import webbrowser
import os

def GetCoordinates(address):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def CreateMap(lat, lon, rad):
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
    
    CreateMap(coords[0], coords[1], radius)

if __name__ == "__main__":
    Main()