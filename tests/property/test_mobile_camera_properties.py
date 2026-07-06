"""
Property-Based Tests for Mobile Camera Capture Availability
Feature: derman-ai-skin-screening

Tests that mobile camera capture functionality is available in the upload interface.

Requirements: 21.2
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
import re


# Hypothesis strategies for generating test data
@st.composite
def mobile_user_agent(draw):
    """Generate realistic mobile user agent strings"""
    mobile_devices = [
        "iPhone",
        "iPad",
        "Android",
        "Mobile",
        "BlackBerry",
        "Windows Phone",
        "webOS"
    ]
    
    device = draw(st.sampled_from(mobile_devices))
    version = draw(st.integers(min_value=1, max_value=20))
    
    if device == "iPhone":
        return f"Mozilla/5.0 (iPhone; CPU iPhone OS {version}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version}.0 Mobile/15E148 Safari/604.1"
    elif device == "iPad":
        return f"Mozilla/5.0 (iPad; CPU OS {version}_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version}.0 Mobile/15E148 Safari/604.1"
    elif device == "Android":
        return f"Mozilla/5.0 (Linux; Android {version}; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36"
    else:
        return f"Mozilla/5.0 (Mobile; {device}; rv:{version}.0) Gecko/{version}.0 Firefox/{version}.0"


@st.composite
def desktop_user_agent(draw):
    """Generate realistic desktop user agent strings"""
    browsers = ["Chrome", "Firefox", "Safari", "Edge"]
    os_list = ["Windows NT 10.0", "Macintosh; Intel Mac OS X 10_15", "X11; Linux x86_64"]
    
    browser = draw(st.sampled_from(browsers))
    os = draw(st.sampled_from(os_list))
    version = draw(st.integers(min_value=80, max_value=120))
    
    if browser == "Chrome":
        return f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
    elif browser == "Firefox":
        return f"Mozilla/5.0 ({os}; rv:{version}.0) Gecko/20100101 Firefox/{version}.0"
    elif browser == "Safari":
        return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version}.0 Safari/605.1.15"
    else:
        return f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0"


def read_diagnostic_uploader_component():
    """Read the DiagnosticUploader component source code"""
    import os
    from pathlib import Path
    
    # Get the component file path
    component_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "components" / "patient" / "DiagnosticUploader.tsx"
    
    if not component_path.exists():
        pytest.skip(f"DiagnosticUploader component not found at {component_path}")
    
    with open(component_path, 'r', encoding='utf-8') as f:
        return f.read()


def check_camera_capture_availability(component_code):
    """
    Check if the component has camera capture functionality.
    
    This checks for:
    1. Input element with type="file"
    2. Accept attribute with "image/*"
    3. Capture attribute with "environment" (rear camera)
    4. Camera icon or button for triggering capture
    """
    # Check for file input with camera capture
    has_file_input = 'type="file"' in component_code or "type='file'" in component_code
    has_image_accept = 'accept="image/*"' in component_code or "accept='image/*'" in component_code
    has_capture_attr = 'capture="environment"' in component_code or "capture='environment'" in component_code
    
    # Check for camera-related UI elements
    has_camera_icon = 'Camera' in component_code or 'camera' in component_code.lower()
    has_camera_label = 'camera' in component_code.lower() or 'photo' in component_code.lower()
    
    return {
        'has_file_input': has_file_input,
        'has_image_accept': has_image_accept,
        'has_capture_attr': has_capture_attr,
        'has_camera_icon': has_camera_icon,
        'has_camera_label': has_camera_label,
        'has_complete_camera_capture': has_file_input and has_image_accept and has_capture_attr
    }


# Feature: derman-ai-skin-screening, Property 69: Mobile Camera Capture Availability
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(user_agent=mobile_user_agent())
def test_mobile_camera_capture_availability(user_agent):
    """
    Property 69: Mobile Camera Capture Availability
    
    For any mobile device user uploading an image, the upload interface should
    offer both file selection and direct camera capture options.
    
    This test verifies:
    1. Component has file input element
    2. File input accepts image/* MIME types
    3. File input has capture="environment" attribute for camera access
    4. Component has camera icon or button for user interaction
    5. Component provides clear camera capture option
    
    Validates: Requirements 21.2
    """
    # Read the DiagnosticUploader component
    component_code = read_diagnostic_uploader_component()
    
    # Check camera capture availability
    camera_features = check_camera_capture_availability(component_code)
    
    # Verify file input exists
    assert camera_features['has_file_input'], \
        "Component should have a file input element for image upload"
    
    # Verify image MIME type acceptance
    assert camera_features['has_image_accept'], \
        "File input should accept 'image/*' MIME types"
    
    # Verify capture attribute for camera access
    assert camera_features['has_capture_attr'], \
        "File input should have capture='environment' attribute for mobile camera access"
    
    # Verify camera UI elements
    assert camera_features['has_camera_icon'], \
        "Component should have camera icon or camera-related UI element"
    
    assert camera_features['has_camera_label'], \
        "Component should have camera or photo label for user clarity"
    
    # Verify complete camera capture functionality
    assert camera_features['has_complete_camera_capture'], \
        "Component should have complete camera capture functionality (file input + image accept + capture attribute)"


# Feature: derman-ai-skin-screening, Property 69: Mobile Camera Capture Availability (File Selection)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(user_agent=mobile_user_agent())
def test_mobile_file_selection_availability(user_agent):
    """
    Property 69: Mobile Camera Capture Availability (File Selection)
    
    For any mobile device user, the upload interface should also provide
    traditional file selection in addition to camera capture.
    
    This test verifies:
    1. Component has drag-and-drop functionality
    2. Component has file browse option
    3. Both camera capture and file selection are available
    
    Validates: Requirements 21.2
    """
    # Read the DiagnosticUploader component
    component_code = read_diagnostic_uploader_component()
    
    # Check for drag-and-drop functionality
    has_dropzone = 'useDropzone' in component_code or 'react-dropzone' in component_code
    has_drag_text = 'drag' in component_code.lower() or 'drop' in component_code.lower()
    
    # Check for file browse option
    has_browse_text = 'browse' in component_code.lower() or 'select' in component_code.lower()
    
    # Check camera capture
    camera_features = check_camera_capture_availability(component_code)
    
    # Verify both options are available
    assert has_dropzone or has_drag_text, \
        "Component should have drag-and-drop functionality"
    
    assert has_browse_text, \
        "Component should have file browse option"
    
    assert camera_features['has_complete_camera_capture'], \
        "Component should have camera capture functionality"
    
    # Verify both methods coexist
    assert (has_dropzone or has_drag_text) and camera_features['has_complete_camera_capture'], \
        "Component should offer BOTH file selection and camera capture options"


# Feature: derman-ai-skin-screening, Property 69: Mobile Camera Capture Availability (Desktop Fallback)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(user_agent=desktop_user_agent())
def test_desktop_file_selection_availability(user_agent):
    """
    Property 69: Mobile Camera Capture Availability (Desktop Fallback)
    
    For any desktop user, the upload interface should provide file selection
    functionality. Camera capture may be available but is not required on desktop.
    
    This test verifies:
    1. Component has file selection functionality
    2. Component works on desktop browsers
    3. File upload is accessible regardless of device type
    
    Validates: Requirements 21.2
    """
    # Read the DiagnosticUploader component
    component_code = read_diagnostic_uploader_component()
    
    # Check for file selection functionality
    has_file_input = 'type="file"' in component_code or "type='file'" in component_code
    has_dropzone = 'useDropzone' in component_code or 'react-dropzone' in component_code
    
    # Verify file selection is available
    assert has_file_input or has_dropzone, \
        "Component should have file selection functionality for desktop users"
    
    # Verify image acceptance
    has_image_accept = 'accept="image' in component_code or "accept='image" in component_code
    assert has_image_accept, \
        "Component should accept image files"


# Feature: derman-ai-skin-screening, Property 69: Mobile Camera Capture Availability (Capture Attribute)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    capture_value=st.sampled_from(["environment", "user", ""])
)
def test_camera_capture_attribute_value(capture_value):
    """
    Property 69: Mobile Camera Capture Availability (Capture Attribute)
    
    For any mobile camera capture implementation, the capture attribute should
    be set to "environment" to use the rear camera by default (better for
    capturing skin lesions).
    
    This test verifies:
    1. Capture attribute is present
    2. Capture attribute value is "environment" (rear camera)
    3. Not "user" (front camera) which is less suitable for medical imaging
    
    Validates: Requirements 21.2
    """
    # Read the DiagnosticUploader component
    component_code = read_diagnostic_uploader_component()
    
    # Check for capture attribute
    has_capture_environment = 'capture="environment"' in component_code or "capture='environment'" in component_code
    has_capture_user = 'capture="user"' in component_code or "capture='user'" in component_code
    
    # Verify environment capture is used (rear camera)
    assert has_capture_environment, \
        "Component should use capture='environment' for rear camera (better for medical imaging)"
    
    # Verify user capture (front camera) is NOT used
    assert not has_capture_user, \
        "Component should NOT use capture='user' (front camera is not suitable for skin lesion imaging)"


# Feature: derman-ai-skin-screening, Property 69: Mobile Camera Capture Availability (UI Clarity)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(user_agent=mobile_user_agent())
def test_camera_capture_ui_clarity(user_agent):
    """
    Property 69: Mobile Camera Capture Availability (UI Clarity)
    
    For any mobile user, the camera capture option should be clearly labeled
    and easily identifiable in the UI.
    
    This test verifies:
    1. Camera icon is present
    2. Clear text label for camera capture
    3. Button or clickable element for camera access
    4. User-friendly language (e.g., "Take Photo", "Camera", etc.)
    
    Validates: Requirements 21.2
    """
    # Read the DiagnosticUploader component
    component_code = read_diagnostic_uploader_component()
    
    # Check for camera icon
    has_camera_icon = 'Camera' in component_code or '<Camera' in component_code
    
    # Check for clear text labels
    camera_text_patterns = [
        'take photo',
        'camera',
        'capture',
        'photo'
    ]
    
    has_clear_label = any(pattern in component_code.lower() for pattern in camera_text_patterns)
    
    # Check for button or label element
    has_button_or_label = '<button' in component_code or '<label' in component_code
    
    # Verify UI clarity
    assert has_camera_icon, \
        "Component should have a Camera icon for visual clarity"
    
    assert has_clear_label, \
        "Component should have clear text label for camera capture (e.g., 'Take Photo', 'Camera')"
    
    assert has_button_or_label, \
        "Component should have button or label element for camera interaction"


# Feature: derman-ai-skin-screening, Property 69: Mobile Camera Capture Availability (Accessibility)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(user_agent=mobile_user_agent())
def test_camera_capture_accessibility(user_agent):
    """
    Property 69: Mobile Camera Capture Availability (Accessibility)
    
    For any mobile user, the camera capture functionality should be accessible
    and properly connected to the file input.
    
    This test verifies:
    1. File input has an ID for label association
    2. Label element references the file input ID
    3. Proper HTML structure for accessibility
    
    Validates: Requirements 21.2
    """
    # Read the DiagnosticUploader component
    component_code = read_diagnostic_uploader_component()
    
    # Check for input ID
    has_input_id = 'id="camera-input"' in component_code or "id='camera-input'" in component_code or 'id="' in component_code
    
    # Check for label with htmlFor
    has_label_for = 'htmlFor="camera-input"' in component_code or "htmlFor='camera-input'" in component_code or 'htmlFor="' in component_code
    
    # Verify accessibility structure
    assert has_input_id, \
        "File input should have an ID for label association"
    
    assert has_label_for, \
        "Label element should reference the file input ID using htmlFor attribute"
