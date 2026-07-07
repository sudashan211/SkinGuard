"""
Debug script to test appointments endpoint
Run this to see the actual error when fetching appointments
"""
import requests
import json

# Get token first (use your actual credentials)
login_data = {
    "email": "sudashanrao@gradaute.utm.my",  # Use the patient email you just created
    "password": "your_password_here"  # Replace with actual password
}

try:
    # Login
    login_response = requests.post(
        "http://localhost:8001/api/auth/login",
        json=login_data
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print(f"✅ Login successful, token: {token[:20]}...")
        
        # Get appointments
        headers = {"Authorization": f"Bearer {token}"}
        appointments_response = requests.get(
            "http://localhost:8001/api/appointments",
            headers=headers
        )
        
        print(f"\nStatus Code: {appointments_response.status_code}")
        print(f"Response: {json.dumps(appointments_response.json(), indent=2)}")
        
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.json())
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
