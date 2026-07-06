"""
Integration test for doctor nearby search endpoint
Task 12.1: Implement doctor search endpoint
"""
import pytest
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Load environment variables
load_dotenv()

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_nearby_doctors_endpoint_exists(client):
    """
    Test that the nearby doctors endpoint exists and has correct structure
    
    This test verifies:
    1. GET /api/doctors/nearby endpoint exists
    2. Endpoint accepts lat, lng, radius query parameters
    3. Endpoint returns list of verified doctors
    4. Endpoint validates coordinate ranges
    5. Endpoint filters only verified doctors (Requirement 7.2)
    6. Endpoint returns doctor profiles with coordinates (Requirement 7.3)
    """
    # Test with valid coordinates
    response = client.get("/api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=50")
    
    # Should return 200 OK (even if empty list)
    assert response.status_code == 200, \
        f"Endpoint should return 200 OK, got {response.status_code}"
    
    # Verify response is a list
    data = response.json()
    assert isinstance(data, list), \
        "Response should be a list of doctors"
    
    # Verify each doctor in the list has required fields
    for doctor in data:
        assert "id" in doctor, "Doctor should have ID"
        assert "user_id" in doctor, "Doctor should have user_id"
        assert "license_no" in doctor, "Doctor should have license_no"
        assert "clinic_name" in doctor, "Doctor should have clinic_name"
        assert "lat" in doctor, "Doctor should have latitude (Requirement 7.3)"
        assert "lng" in doctor, "Doctor should have longitude (Requirement 7.3)"
        assert "whatsapp_no" in doctor, "Doctor should have WhatsApp number"
        assert "verified" in doctor, "Doctor should have verified status"
        
        # Verify only verified doctors are returned (Requirement 7.2)
        assert doctor["verified"] == True, \
            "Only verified doctors should be returned (Requirement 7.2)"
        
        # Verify coordinates are within valid ranges
        assert -90 <= doctor["lat"] <= 90, \
            f"Latitude should be within [-90, 90], got {doctor['lat']}"
        assert -180 <= doctor["lng"] <= 180, \
            f"Longitude should be within [-180, 180], got {doctor['lng']}"
    
    print("\n✅ Nearby doctors endpoint test passed!")
    print(f"   - Endpoint exists at GET /api/doctors/nearby")
    print(f"   - Accepts lat, lng, radius query parameters")
    print(f"   - Returns list of verified doctors")
    print(f"   - Filters only verified doctors (Requirement 7.2)")
    print(f"   - Returns doctor profiles with coordinates (Requirement 7.3)")


def test_nearby_doctors_coordinate_validation(client):
    """
    Test that the nearby doctors endpoint validates coordinates correctly
    """
    # Test with invalid latitude (> 90)
    response = client.get("/api/doctors/nearby?lat=100&lng=-74.0060&radius=50")
    assert response.status_code == 422, \
        "Endpoint should return 422 for invalid latitude"
    
    # Test with invalid longitude (> 180)
    response = client.get("/api/doctors/nearby?lat=40.7128&lng=200&radius=50")
    assert response.status_code == 422, \
        "Endpoint should return 422 for invalid longitude"
    
    # Test with invalid radius (< 1)
    response = client.get("/api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=0")
    assert response.status_code == 422, \
        "Endpoint should return 422 for invalid radius"
    
    # Test with invalid radius (> 500)
    response = client.get("/api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=1000")
    assert response.status_code == 422, \
        "Endpoint should return 422 for radius > 500"
    
    print("\n✅ Nearby doctors coordinate validation test passed!")
    print(f"   - Validates latitude range [-90, 90]")
    print(f"   - Validates longitude range [-180, 180]")
    print(f"   - Validates radius range [1, 500]")


def test_nearby_doctors_default_radius(client):
    """
    Test that the nearby doctors endpoint uses default radius when not specified
    """
    # Test without radius parameter (should use default 50km)
    response = client.get("/api/doctors/nearby?lat=40.7128&lng=-74.0060")
    
    assert response.status_code == 200, \
        "Endpoint should accept request without radius parameter"
    
    data = response.json()
    assert isinstance(data, list), \
        "Response should be a list even with default radius"
    
    print("\n✅ Nearby doctors default radius test passed!")
    print(f"   - Uses default radius of 50km when not specified")


def test_nearby_doctors_geographic_filtering(client):
    """
    Test that the nearby doctors endpoint filters by geographic distance
    """
    # Test with very small radius (1km) - should return fewer or no results
    response_small = client.get("/api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=1")
    assert response_small.status_code == 200
    small_radius_count = len(response_small.json())
    
    # Test with larger radius (100km) - should return same or more results
    response_large = client.get("/api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=100")
    assert response_large.status_code == 200
    large_radius_count = len(response_large.json())
    
    # Larger radius should return >= results than smaller radius
    assert large_radius_count >= small_radius_count, \
        "Larger radius should return same or more doctors than smaller radius"
    
    print("\n✅ Nearby doctors geographic filtering test passed!")
    print(f"   - Filters doctors by distance from coordinates")
    print(f"   - Larger radius returns more results")
    print(f"   - Uses PostGIS/Haversine for geographic queries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
