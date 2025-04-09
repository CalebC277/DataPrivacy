import googlemaps
import requests

def find(api_key, latitude, longitude, radius, category):
    endpoint = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{latitude}, {longitude}',
        'radius': radius,
        'category': category,
        'api_key': api_key
    }

    response = requests.get(endpoint, params=params)
    results = response.json().get('results', [])

    return results

if __name__ == '__main__':
    api_key = 'KEY******'
    latitude = 39.2904
    longitude = 76.6122
    radius = 1000
    categories = 'school|hospital|park|restaurant'

    places = find(api_key, latitude, longitude, radius, categories)

    for place in places:
        print(place['name'], place['vicinity'])