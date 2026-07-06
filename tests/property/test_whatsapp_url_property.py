"""
Property-Based Tests for WhatsApp URL Generation
Feature: derman-ai-skin-screening

Tests WhatsApp URL format correctness property.

Requirements: 7.5
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import MagicMock
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing anything that uses it
sys.modules['app.database'] = MagicMock()

from app.models import DoctorResponse


# Hypothesis strategies for generating test data
@st.composite
def whatsapp_number(draw):
    """Generate valid WhatsApp numbers in various formats"""
    # Generate country code (1-3 digits)
    country_code = draw(st.integers(min_value=1, max_value=999))
    # Generate phone number (7-12 digits)
    phone_number = draw(st.integers(min_value=1000000, max_value=999999999999))
    
    # Randomly include '+' prefix or not
    include_plus = draw(st.booleans())
    
    if include_plus:
        return f"+{country_code}{phone_number}"
    else:
        return f"{country_code}{phone_number}"


@st.composite
def doctor_data_with_whatsapp(draw):
    """Generate doctor data for testing WhatsApp URL"""
    return {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "license_no": f"LIC{draw(st.integers(min_value=100000, max_value=999999))}",
        "clinic_name": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs')))),
        "lat": draw(st.floats(min_value=-90, max_value=90)),
        "lng": draw(st.floats(min_value=-180, max_value=180)),
        "whatsapp_no": draw(whatsapp_number()),
        "specialization": draw(st.sampled_from(["Dermatology", "Oncology", "General Practice"])),
        "average_rating": draw(st.floats(min_value=0.0, max_value=5.0)),
        "review_count": draw(st.integers(min_value=0, max_value=1000)),
        "verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


# Feature: derman-ai-skin-screening, Property 20: WhatsApp URL Format
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(doctor=doctor_data_with_whatsapp())
def test_whatsapp_url_format(doctor):
    """
    Property 20: WhatsApp URL Format
    
    For any doctor's WhatsApp contact, the generated URL should match the format
    "https://wa.me/{whatsapp_no}?text=I would like to share my Derman Report"
    where {whatsapp_no} is the doctor's WhatsApp number.
    
    This test verifies:
    1. URL starts with "https://wa.me/"
    2. WhatsApp number is correctly formatted (no '+' prefix)
    3. Message parameter is correctly URL-encoded
    4. Default message is "I would like to share my Derman Report"
    5. URL is valid and parseable
    
    Validates: Requirements 7.5
    """
    # Create DoctorResponse instance
    doctor_response = DoctorResponse(**doctor)
    
    # Verify whatsapp_url is automatically generated
    assert doctor_response.whatsapp_url is not None, \
        "WhatsApp URL should be automatically generated"
    
    # Parse the URL
    parsed_url = urlparse(doctor_response.whatsapp_url)
    
    # Verify URL scheme is https
    assert parsed_url.scheme == "https", \
        f"URL scheme should be 'https', got '{parsed_url.scheme}'"
    
    # Verify domain is wa.me
    assert parsed_url.netloc == "wa.me", \
        f"URL domain should be 'wa.me', got '{parsed_url.netloc}'"
    
    # Verify path contains the phone number
    path = parsed_url.path.lstrip('/')
    
    # The phone number should not have '+' prefix
    assert not path.startswith('+'), \
        f"Phone number in URL should not have '+' prefix, got '{path}'"
    
    # Verify the phone number matches (after removing '+' from original)
    expected_number = doctor["whatsapp_no"].lstrip('+')
    assert path == expected_number, \
        f"Phone number mismatch: expected '{expected_number}', got '{path}'"
    
    # Verify query parameters
    query_params = parse_qs(parsed_url.query)
    
    # Verify 'text' parameter exists
    assert 'text' in query_params, \
        "URL should contain 'text' query parameter"
    
    # Verify message content (URL-decoded)
    message = unquote(query_params['text'][0])
    expected_message = "I would like to share my Derman Report"
    
    assert message == expected_message, \
        f"Message mismatch: expected '{expected_message}', got '{message}'"
    
    # Verify complete URL format
    expected_url_pattern = f"https://wa.me/{expected_number}?text="
    assert doctor_response.whatsapp_url.startswith(expected_url_pattern), \
        f"URL should start with '{expected_url_pattern}'"


# Feature: derman-ai-skin-screening, Property 20: WhatsApp URL Format (Custom Message)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    doctor=doctor_data_with_whatsapp(),
    custom_message=st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs', 'P')))
)
def test_whatsapp_url_format_custom_message(doctor, custom_message):
    """
    Property 20: WhatsApp URL Format (Custom Message)
    
    For any doctor's WhatsApp contact with a custom message, the generated URL
    should correctly encode the custom message in the URL.
    
    This test verifies:
    1. Custom messages are properly URL-encoded
    2. Special characters are handled correctly
    3. Spaces are encoded properly
    4. The get_whatsapp_url method accepts custom messages
    
    Validates: Requirements 7.5
    """
    # Create DoctorResponse instance
    doctor_response = DoctorResponse(**doctor)
    
    # Generate URL with custom message
    custom_url = doctor_response.get_whatsapp_url(message=custom_message)
    
    # Parse the URL
    parsed_url = urlparse(custom_url)
    
    # Verify URL structure
    assert parsed_url.scheme == "https", "URL scheme should be 'https'"
    assert parsed_url.netloc == "wa.me", "URL domain should be 'wa.me'"
    
    # Verify query parameters
    query_params = parse_qs(parsed_url.query)
    assert 'text' in query_params, "URL should contain 'text' query parameter"
    
    # Verify custom message content (URL-decoded)
    decoded_message = unquote(query_params['text'][0])
    assert decoded_message == custom_message, \
        f"Custom message mismatch: expected '{custom_message}', got '{decoded_message}'"


# Feature: derman-ai-skin-screening, Property 20: WhatsApp URL Format (Edge Cases)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    country_code=st.integers(min_value=1, max_value=999),
    phone_number=st.integers(min_value=1000000, max_value=999999999999)
)
def test_whatsapp_url_format_edge_cases(country_code, phone_number):
    """
    Property 20: WhatsApp URL Format (Edge Cases)
    
    For any valid phone number format, the WhatsApp URL should be correctly
    generated with proper number formatting.
    
    This test verifies:
    1. Numbers with '+' prefix are handled correctly
    2. Numbers without '+' prefix are handled correctly
    3. Various country codes are supported
    4. Various phone number lengths are supported
    
    Validates: Requirements 7.5
    """
    # Test with '+' prefix
    whatsapp_with_plus = f"+{country_code}{phone_number}"
    doctor_data_plus = {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "license_no": "LIC123456",
        "clinic_name": "Test Clinic",
        "lat": 0.0,
        "lng": 0.0,
        "whatsapp_no": whatsapp_with_plus,
        "specialization": "Dermatology",
        "average_rating": 4.5,
        "review_count": 10,
        "verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    doctor_response_plus = DoctorResponse(**doctor_data_plus)
    
    # Verify URL is generated
    assert doctor_response_plus.whatsapp_url is not None
    
    # Parse URL
    parsed_url_plus = urlparse(doctor_response_plus.whatsapp_url)
    path_plus = parsed_url_plus.path.lstrip('/')
    
    # Verify '+' is removed from URL
    assert not path_plus.startswith('+'), \
        "Phone number in URL should not have '+' prefix"
    
    # Verify number matches (without '+')
    expected_number = f"{country_code}{phone_number}"
    assert path_plus == expected_number, \
        f"Phone number mismatch: expected '{expected_number}', got '{path_plus}'"
    
    # Test without '+' prefix
    whatsapp_without_plus = f"{country_code}{phone_number}"
    doctor_data_no_plus = {
        **doctor_data_plus,
        "id": str(uuid.uuid4()),
        "whatsapp_no": whatsapp_without_plus
    }
    
    doctor_response_no_plus = DoctorResponse(**doctor_data_no_plus)
    
    # Verify URL is generated
    assert doctor_response_no_plus.whatsapp_url is not None
    
    # Parse URL
    parsed_url_no_plus = urlparse(doctor_response_no_plus.whatsapp_url)
    path_no_plus = parsed_url_no_plus.path.lstrip('/')
    
    # Verify number matches
    assert path_no_plus == expected_number, \
        f"Phone number mismatch: expected '{expected_number}', got '{path_no_plus}'"
    
    # Verify both URLs are identical ('+' prefix should not affect final URL)
    assert doctor_response_plus.whatsapp_url == doctor_response_no_plus.whatsapp_url, \
        "URLs should be identical regardless of '+' prefix in input"


# Feature: derman-ai-skin-screening, Property 20: WhatsApp URL Format (URL Validity)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(doctor=doctor_data_with_whatsapp())
def test_whatsapp_url_validity(doctor):
    """
    Property 20: WhatsApp URL Format (URL Validity)
    
    For any doctor's WhatsApp URL, the URL should be valid and properly formatted
    according to URL standards.
    
    This test verifies:
    1. URL is a valid HTTP URL
    2. URL can be parsed without errors
    3. URL contains all required components
    4. URL is properly encoded
    
    Validates: Requirements 7.5
    """
    # Create DoctorResponse instance
    doctor_response = DoctorResponse(**doctor)
    
    # Verify URL exists
    assert doctor_response.whatsapp_url is not None
    assert isinstance(doctor_response.whatsapp_url, str)
    assert len(doctor_response.whatsapp_url) > 0
    
    # Verify URL can be parsed
    try:
        parsed_url = urlparse(doctor_response.whatsapp_url)
    except Exception as e:
        pytest.fail(f"Failed to parse WhatsApp URL: {e}")
    
    # Verify all required URL components are present
    assert parsed_url.scheme, "URL should have a scheme"
    assert parsed_url.netloc, "URL should have a network location"
    assert parsed_url.path, "URL should have a path"
    assert parsed_url.query, "URL should have query parameters"
    
    # Verify URL is absolute (not relative)
    assert parsed_url.scheme in ['http', 'https'], \
        f"URL should use HTTP or HTTPS scheme, got '{parsed_url.scheme}'"
    
    # Verify URL doesn't contain invalid characters
    invalid_chars = [' ', '\n', '\r', '\t']
    for char in invalid_chars:
        assert char not in doctor_response.whatsapp_url, \
            f"URL should not contain invalid character '{repr(char)}'"
    
    # Verify URL is properly encoded (no unencoded spaces in query)
    query_part = doctor_response.whatsapp_url.split('?', 1)[1] if '?' in doctor_response.whatsapp_url else ''
    assert ' ' not in query_part, \
        "Query parameters should be URL-encoded (no raw spaces)"
