"""
Test nearby doctors endpoint with coordinates (0, 0)
"""
import requests

# Test with (0, 0) coordinates like the frontend does
url = "http://localhost:8001/api/doctors/nearby"
params = {
    "lat": 0,
    "lng": 0,
    "radius": 50
}

try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        doctors = response.json()
        print(f"Found {len(doctors)} doctors at (0, 0) with radius 50km")
    else:
        print(f"Error: {response.json()}")
    
    # Now test with a much larger radius
    params["radius"] = 20000  # 20,000 km
    response2 = requests.get(url, params=params)
    if response2.status_code == 200:
        doctors2 = response2.json()
        print(f"Found {len(doctors2)} doctors at (0, 0) with radius 20,000km")
    
except Exception as e:
    print(f"Error: {e}")
