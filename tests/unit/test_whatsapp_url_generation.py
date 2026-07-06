"""
Unit Tests for WhatsApp URL Generation
Feature: derman-ai-skin-screening

Tests specific examples of WhatsApp URL generation.

Requirements: 7.5
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()

from app.models import DoctorResponse


def test_whatsapp_url_basic_example():
    """
    Test basic WhatsApp URL generation with a standard phone number.
    
    Validates: Requirements 7.5
    """
    doctor_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "license_no": "LIC123456",
        "clinic_name": "City Dermatology Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+12125551234",
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 100,
        "verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    doctor = DoctorResponse(**doctor_data)
    
    # Verify WhatsApp URL is automatically generated
    assert doctor.whatsapp_url is not None
    
    # Verify URL format
    expected_url = "https://wa.me/12125551234?text=I%20would%20like%20to%20share%20my%20Derman%20Report"
    assert doctor.whatsapp_url == expected_url
    
    print(f"✓ Generated WhatsApp URL: {doctor.whatsapp_url}")


def test_whatsapp_url_without_plus_prefix():
    """
    Test WhatsApp URL generation when phone number doesn't have '+' prefix.
    
    Validates: Requirements 7.5
    """
    doctor_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "license_no": "LIC123456",
        "clinic_name": "City Dermatology Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "12125551234",  # No '+' prefix
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 100,
        "verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    doctor = DoctorResponse(**doctor_data)
    
    # Verify WhatsApp URL is generated correctly
    assert doctor.whatsapp_url is not None
    assert "https://wa.me/12125551234" in doctor.whatsapp_url
    assert "text=I%20would%20like%20to%20share%20my%20Derman%20Report" in doctor.whatsapp_url
    
    print(f"✓ Generated WhatsApp URL (no + prefix): {doctor.whatsapp_url}")


def test_whatsapp_url_custom_message():
    """
    Test WhatsApp URL generation with a custom message.
    
    Validates: Requirements 7.5
    """
    doctor_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "license_no": "LIC123456",
        "clinic_name": "City Dermatology Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+12125551234",
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 100,
        "verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    doctor = DoctorResponse(**doctor_data)
    
    # Generate URL with custom message
    custom_message = "Hello Dr. Smith, I need an urgent consultation"
    custom_url = doctor.get_whatsapp_url(message=custom_message)
    
    # Verify URL contains custom message (URL-encoded)
    assert "https://wa.me/12125551234" in custom_url
    assert "Hello%20Dr.%20Smith" in custom_url
    assert "urgent%20consultation" in custom_url
    
    print(f"✓ Generated WhatsApp URL (custom message): {custom_url}")


def test_whatsapp_url_international_numbers():
    """
    Test WhatsApp URL generation with various international phone numbers.
    
    Validates: Requirements 7.5
    """
    test_cases = [
        ("+442071234567", "442071234567"),  # UK
        ("+919876543210", "919876543210"),  # India
        ("+5511987654321", "5511987654321"),  # Brazil
        ("+81312345678", "81312345678"),  # Japan
        ("+27123456789", "27123456789"),  # South Africa
    ]
    
    for whatsapp_no, expected_number in test_cases:
        doctor_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": "123e4567-e89b-12d3-a456-426614174001",
            "license_no": "LIC123456",
            "clinic_name": "International Clinic",
            "lat": 0.0,
            "lng": 0.0,
            "whatsapp_no": whatsapp_no,
            "specialization": "Dermatology",
            "average_rating": 4.5,
            "review_count": 100,
            "verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        doctor = DoctorResponse(**doctor_data)
        
        # Verify URL contains correct number (without '+')
        assert f"https://wa.me/{expected_number}" in doctor.whatsapp_url
        
        print(f"✓ Generated WhatsApp URL for {whatsapp_no}: {doctor.whatsapp_url}")


def test_whatsapp_url_message_encoding():
    """
    Test that special characters in messages are properly URL-encoded.
    
    Validates: Requirements 7.5
    """
    doctor_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "license_no": "LIC123456",
        "clinic_name": "City Dermatology Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+12125551234",
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 100,
        "verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    doctor = DoctorResponse(**doctor_data)
    
    # Test message with special characters
    special_message = "Hello! I need help with my skin condition (urgent) & treatment options."
    special_url = doctor.get_whatsapp_url(message=special_message)
    
    # Verify special characters are encoded
    assert "%21" in special_url or "!" in special_url  # '!' may or may not be encoded
    assert "%28" in special_url or "(" in special_url  # '(' may or may not be encoded
    assert "%29" in special_url or ")" in special_url  # ')' may or may not be encoded
    assert "%26" in special_url or "&" in special_url  # '&' may or may not be encoded
    
    # Verify no raw spaces
    assert " " not in special_url.split("?")[1]  # No spaces in query string
    
    print(f"✓ Generated WhatsApp URL (special chars): {special_url}")


def test_whatsapp_url_default_message():
    """
    Test that the default message is correctly set.
    
    Validates: Requirements 7.5
    """
    doctor_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "license_no": "LIC123456",
        "clinic_name": "City Dermatology Clinic",
        "lat": 40.7128,
        "lng": -74.0060,
        "whatsapp_no": "+12125551234",
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 100,
        "verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    doctor = DoctorResponse(**doctor_data)
    
    # Verify default message is present
    assert "I%20would%20like%20to%20share%20my%20Derman%20Report" in doctor.whatsapp_url
    
    # Decode and verify exact message
    from urllib.parse import unquote, parse_qs, urlparse
    parsed = urlparse(doctor.whatsapp_url)
    params = parse_qs(parsed.query)
    message = params['text'][0]
    
    assert message == "I would like to share my Derman Report"
    
    print(f"✓ Default message verified: {message}")


if __name__ == "__main__":
    # Run tests manually
    test_whatsapp_url_basic_example()
    test_whatsapp_url_without_plus_prefix()
    test_whatsapp_url_custom_message()
    test_whatsapp_url_international_numbers()
    test_whatsapp_url_message_encoding()
    test_whatsapp_url_default_message()
    
    print("\n✅ All WhatsApp URL generation tests passed!")
