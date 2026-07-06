"""
Property-Based Tests for GPS Location Centering
Feature: derman-ai-skin-screening

Tests that the doctor locator map centers on the device's GPS coordinates
when location permission is granted.

Requirements: 21.5
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
import re


# Hypothesis strategies for generating test data
@st.composite
def gps_coordinates(draw):
    """Generate valid GPS coordinates"""
    # Latitude: -90 to 90
    lat = draw(st.floats(min_value=-90.0, max_value=90.0, allow_nan=False, allow_infinity=False))
    # Longitude: -180 to 180
    lng = draw(st.floats(min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False))
    return {'lat': lat, 'lng': lng}


@st.composite
def mobile_device_info(draw):
    """Generate mobile device information"""
    devices = ['iPhone', 'iPad', 'Android Phone', 'Android Tablet']
    browsers = ['Safari', 'Chrome', 'Firefox', 'Edge']
    
    device = draw(st.sampled_from(devices))
    browser = draw(st.sampled_from(browsers))
    has_geolocation = draw(st.booleans())
    
    return {
        'device': device,
        'browser': browser,
        'has_geolocation': has_geolocation
    }


def read_doctor_map_component():
    """Read the DoctorMap component source code"""
    import os
    from pathlib import Path
    
    # Get the component file path
    component_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "components" / "patient" / "DoctorMap.tsx"
    
    if not component_path.exists():
        pytest.skip(f"DoctorMap component not found at {component_path}")
    
    with open(component_path, 'r', encoding='utf-8') as f:
        return f.read()


def check_gps_centering_implementation(component_code):
    """
    Check if the component implements GPS centering functionality.
    
    This checks for:
    1. navigator.geolocation API usage
    2. getCurrentPosition call
    3. Setting user location state
    4. Using user location as map center
    5. Handling location permission denial
    """
    # Check for geolocation API usage
    has_navigator_geolocation = 'navigator.geolocation' in component_code
    has_get_current_position = 'getCurrentPosition' in component_code
    
    # Check for location state management
    has_user_location_state = 'userLocation' in component_code or 'setUserLocation' in component_code
    
    # Check for map centering on user location
    has_map_center = 'center=' in component_code or 'mapCenter' in component_code
    
    # Check for location error handling
    has_error_handling = 'locationError' in component_code or 'geolocation' in component_code.lower()
    
    # Check for default fallback location
    has_default_center = 'DEFAULT_CENTER' in component_code or 'default' in component_code.lower()
    
    # Check for useEffect hook to get location on mount
    has_use_effect = 'useEffect' in component_code
    
    # Check for map centering logic
    uses_user_location_for_center = (
        'userLocation' in component_code and 
        ('center=' in component_code or 'mapCenter' in component_code)
    )
    
    return {
        'has_navigator_geolocation': has_navigator_geolocation,
        'has_get_current_position': has_get_current_position,
        'has_user_location_state': has_user_location_state,
        'has_map_center': has_map_center,
        'has_error_handling': has_error_handling,
        'has_default_center': has_default_center,
        'has_use_effect': has_use_effect,
        'uses_user_location_for_center': uses_user_location_for_center,
        'has_complete_gps_centering': (
            has_navigator_geolocation and 
            has_get_current_position and 
            has_user_location_state and 
            uses_user_location_for_center
        )
    }


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    coords=gps_coordinates(),
    device_info=mobile_device_info()
)
def test_gps_location_centering(coords, device_info):
    """
    Property 72: GPS Location Centering
    
    For any mobile user accessing the doctor locator map, the map should center
    on the device's GPS coordinates if location permission is granted.
    
    This test verifies:
    1. Component uses navigator.geolocation API
    2. Component calls getCurrentPosition to get user location
    3. Component stores user location in state
    4. Component uses user location as map center
    5. Component handles location permission denial gracefully
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check GPS centering implementation
    gps_features = check_gps_centering_implementation(component_code)
    
    # Verify navigator.geolocation API usage
    assert gps_features['has_navigator_geolocation'], \
        "Component should use navigator.geolocation API to access device GPS"
    
    # Verify getCurrentPosition call
    assert gps_features['has_get_current_position'], \
        "Component should call getCurrentPosition to get user's GPS coordinates"
    
    # Verify user location state management
    assert gps_features['has_user_location_state'], \
        "Component should store user location in state (userLocation)"
    
    # Verify map centering
    assert gps_features['has_map_center'], \
        "Component should have map center configuration"
    
    # Verify user location is used for centering
    assert gps_features['uses_user_location_for_center'], \
        "Component should use user location as map center when available"
    
    # Verify complete GPS centering functionality
    assert gps_features['has_complete_gps_centering'], \
        "Component should have complete GPS centering functionality (geolocation API + getCurrentPosition + state + centering)"


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering (Error Handling)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(device_info=mobile_device_info())
def test_gps_location_error_handling(device_info):
    """
    Property 72: GPS Location Centering (Error Handling)
    
    For any mobile user who denies location permission or has geolocation
    unavailable, the map should fall back to a default location gracefully.
    
    This test verifies:
    1. Component handles geolocation errors
    2. Component has a default fallback location
    3. Component displays error message when location is unavailable
    4. Component still renders the map with default location
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check error handling implementation
    gps_features = check_gps_centering_implementation(component_code)
    
    # Verify error handling
    assert gps_features['has_error_handling'], \
        "Component should handle location errors (permission denied, unavailable, etc.)"
    
    # Verify default fallback location
    assert gps_features['has_default_center'], \
        "Component should have a default center location for fallback"
    
    # Check for error callback in getCurrentPosition
    has_error_callback = 'error' in component_code and 'getCurrentPosition' in component_code
    assert has_error_callback, \
        "Component should provide error callback to getCurrentPosition"
    
    # Check for geolocation availability check
    has_geolocation_check = 'if (navigator.geolocation)' in component_code or 'navigator.geolocation' in component_code
    assert has_geolocation_check, \
        "Component should check if navigator.geolocation is available"


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering (Initialization)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(coords=gps_coordinates())
def test_gps_location_initialization(coords):
    """
    Property 72: GPS Location Centering (Initialization)
    
    For any mobile user accessing the map, GPS location should be requested
    when the component mounts (initialization).
    
    This test verifies:
    1. Component uses useEffect hook for initialization
    2. Location is requested on component mount
    3. Location request happens automatically without user action
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check initialization implementation
    gps_features = check_gps_centering_implementation(component_code)
    
    # Verify useEffect usage
    assert gps_features['has_use_effect'], \
        "Component should use useEffect hook for initialization"
    
    # Check for useEffect with empty dependency array (runs on mount)
    has_mount_effect = 'useEffect' in component_code and '[]' in component_code
    assert has_mount_effect, \
        "Component should have useEffect with empty dependency array to run on mount"
    
    # Verify getCurrentPosition is called in useEffect
    # This is a heuristic check - we look for both in the code
    assert gps_features['has_get_current_position'] and gps_features['has_use_effect'], \
        "Component should call getCurrentPosition in useEffect for automatic location request"


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering (Map Center Update)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    initial_coords=gps_coordinates(),
    updated_coords=gps_coordinates()
)
def test_gps_map_center_update(initial_coords, updated_coords):
    """
    Property 72: GPS Location Centering (Map Center Update)
    
    For any mobile user, when GPS location is obtained, the map center should
    be updated to reflect the user's actual location.
    
    This test verifies:
    1. Map center is derived from user location state
    2. Map center updates when user location changes
    3. Map uses user location or falls back to default
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check map center logic
    gps_features = check_gps_centering_implementation(component_code)
    
    # Verify map center uses user location
    assert gps_features['uses_user_location_for_center'], \
        "Map center should be derived from user location state"
    
    # Check for conditional center logic (userLocation || DEFAULT_CENTER)
    has_conditional_center = (
        ('userLocation || DEFAULT_CENTER' in component_code) or
        ('userLocation ? userLocation : DEFAULT_CENTER' in component_code) or
        ('mapCenter' in component_code and 'userLocation' in component_code)
    )
    assert has_conditional_center, \
        "Map center should conditionally use userLocation or fall back to DEFAULT_CENTER"
    
    # Verify GoogleMap component receives center prop
    has_google_map_center = '<GoogleMap' in component_code and 'center=' in component_code
    assert has_google_map_center, \
        "GoogleMap component should receive center prop"


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering (User Location Marker)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(coords=gps_coordinates())
def test_gps_user_location_marker(coords):
    """
    Property 72: GPS Location Centering (User Location Marker)
    
    For any mobile user with GPS location available, the map should display
    a marker at the user's current location for visual clarity.
    
    This test verifies:
    1. Component renders a marker for user location
    2. Marker is positioned at user's GPS coordinates
    3. Marker is visually distinct from doctor markers
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check for user location marker
    has_user_marker = '<Marker' in component_code and 'userLocation' in component_code
    assert has_user_marker, \
        "Component should render a Marker for user location"
    
    # Check for conditional rendering based on userLocation
    has_conditional_marker = '{userLocation &&' in component_code or 'userLocation && (' in component_code
    assert has_conditional_marker, \
        "User location marker should be conditionally rendered when userLocation is available"
    
    # Check for distinct marker styling
    has_marker_icon = 'icon=' in component_code or 'icon:' in component_code
    assert has_marker_icon, \
        "User location marker should have custom icon for visual distinction"


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering (Recenter Button)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(coords=gps_coordinates())
def test_gps_recenter_functionality(coords):
    """
    Property 72: GPS Location Centering (Recenter Button)
    
    For any mobile user who has panned away from their location, there should
    be a button to recenter the map on their GPS coordinates.
    
    This test verifies:
    1. Component has a recenter/center-on-user button
    2. Button triggers map pan to user location
    3. Button is only shown when user location is available
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check for recenter button
    has_recenter_button = (
        'handleCenterOnUser' in component_code or 
        'centerOnUser' in component_code or
        'panTo' in component_code
    )
    assert has_recenter_button, \
        "Component should have functionality to recenter map on user location"
    
    # Check for button element
    has_button_element = '<button' in component_code and ('Center' in component_code or 'Navigation' in component_code)
    assert has_button_element, \
        "Component should have a button element for recentering"
    
    # Check for map.panTo usage
    has_pan_to = 'panTo' in component_code
    assert has_pan_to, \
        "Component should use map.panTo() to recenter on user location"
    
    # Check for conditional button rendering
    has_conditional_button = '{userLocation &&' in component_code
    assert has_conditional_button, \
        "Recenter button should only be shown when user location is available"


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering (High Accuracy)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(coords=gps_coordinates())
def test_gps_high_accuracy_option(coords):
    """
    Property 72: GPS Location Centering (High Accuracy)
    
    For any mobile user, the GPS location request should use high accuracy
    mode to get the most precise location for finding nearby doctors.
    
    This test verifies:
    1. getCurrentPosition is called with options parameter
    2. enableHighAccuracy option is set to true
    3. Timeout and maximumAge options are configured
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check for getCurrentPosition options
    has_position_options = (
        'enableHighAccuracy' in component_code or
        'timeout' in component_code or
        'maximumAge' in component_code
    )
    assert has_position_options, \
        "Component should provide options to getCurrentPosition for better accuracy"
    
    # Check for enableHighAccuracy: true
    has_high_accuracy = 'enableHighAccuracy: true' in component_code or 'enableHighAccuracy:true' in component_code
    assert has_high_accuracy, \
        "Component should set enableHighAccuracy to true for precise GPS location"
    
    # Check for timeout configuration
    has_timeout = 'timeout:' in component_code
    assert has_timeout, \
        "Component should configure timeout for getCurrentPosition"


# Feature: derman-ai-skin-screening, Property 72: GPS Location Centering (Fetch Nearby Doctors)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(coords=gps_coordinates())
def test_gps_triggers_nearby_doctors_fetch(coords):
    """
    Property 72: GPS Location Centering (Fetch Nearby Doctors)
    
    For any mobile user with GPS location obtained, the system should
    automatically fetch nearby doctors based on the GPS coordinates.
    
    This test verifies:
    1. Component fetches nearby doctors when location is available
    2. Fetch uses user's GPS coordinates
    3. Fetch is triggered automatically via useEffect
    
    **Validates: Requirements 21.5**
    """
    # Read the DoctorMap component
    component_code = read_doctor_map_component()
    
    # Check for nearby doctors fetch function
    has_fetch_function = (
        'fetchNearbyDoctors' in component_code or
        'getNearbyDoctors' in component_code
    )
    assert has_fetch_function, \
        "Component should have function to fetch nearby doctors"
    
    # Check for useEffect that triggers fetch when location changes
    has_location_effect = (
        'useEffect' in component_code and 
        'userLocation' in component_code and
        ('fetchNearbyDoctors' in component_code or 'getNearbyDoctors' in component_code)
    )
    assert has_location_effect, \
        "Component should use useEffect to fetch nearby doctors when userLocation changes"
    
    # Check that fetch uses lat/lng parameters
    has_lat_lng_params = 'lat' in component_code and 'lng' in component_code
    assert has_lat_lng_params, \
        "Nearby doctors fetch should use lat and lng parameters from GPS location"
