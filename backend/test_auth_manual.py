"""
Manual test script for authentication endpoints
Run this after setting up .env file to verify the implementation
"""
import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_signup():
    """Test user signup"""
    data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "role": "patient"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
    print_response("User Signup", response)
    return response.status_code == 201, data["email"]


def test_login(email):
    """Test user login"""
    data = {
        "email": email,
        "password": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print_response("User Login", response)
    
    if response.status_code == 200:
        return True, response.json()["access_token"]
    return False, None


def test_get_me(token):
    """Test get current user"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print_response("Get Current User", response)
    return response.status_code == 200


def test_logout(token):
    """Test logout"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    print_response("Logout", response)
    return response.status_code == 200


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SkinGuard Authentication API Tests")
    print("="*60)
    print("\nMake sure the server is running: python -m app.main")
    print("And .env file is configured with Supabase credentials")
    input("\nPress Enter to continue...")
    
    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed. Is the server running?")
        return
    
    print("\n✅ Health check passed")
    
    # Test signup
    success, email = test_signup()
    if not success:
        print("\n❌ Signup failed")
        return
    
    print("\n✅ Signup passed")
    
    # Test login
    success, token = test_login(email)
    if not success:
        print("\n❌ Login failed")
        return
    
    print("\n✅ Login passed")
    
    # Test get current user
    if not test_get_me(token):
        print("\n❌ Get current user failed")
        return
    
    print("\n✅ Get current user passed")
    
    # Test logout
    if not test_logout(token):
        print("\n❌ Logout failed")
        return
    
    print("\n✅ Logout passed")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)


if __name__ == "__main__":
    main()
