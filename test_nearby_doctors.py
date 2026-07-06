"""
Test the nearby doctors endpoint
"""
import requests

# Test with default Singapore coordinates
url = "http://localhost:8001/api/doctors/nearby"
params = {
    "lat": 1.3521,
    "lng": 103.8198,
    "radius": 50
}

try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        doctors = response.json()
        print(f"\nFound {len(doctors)} doctors:")
        for doctor in doctors:
            print(f"  - {doctor.get('clinic_name')} (verified: {doctor.get('verified')})")
    
except Exception as e:
    print(f"Error: {e}")
