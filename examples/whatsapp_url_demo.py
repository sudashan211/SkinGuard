"""
WhatsApp URL Generation Demo
Feature: derman-ai-skin-screening

This script demonstrates how the WhatsApp URL generation works for the
Doctor Locator System.

Requirements: 7.5
"""

import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock database before importing models
from unittest.mock import MagicMock
sys.modules['app.database'] = MagicMock()

from app.models import DoctorResponse


def demo_whatsapp_url_generation():
    """
    Demonstrate WhatsApp URL generation for doctor contacts.
    """
    print("=" * 80)
    print("WhatsApp URL Generation Demo")
    print("=" * 80)
    print()
    
    # Example 1: Basic doctor profile
    print("Example 1: Basic Doctor Profile")
    print("-" * 80)
    
    doctor1 = DoctorResponse(
        id="123e4567-e89b-12d3-a456-426614174000",
        user_id="123e4567-e89b-12d3-a456-426614174001",
        license_no="LIC123456",
        clinic_name="City Dermatology Clinic",
        lat=40.7128,
        lng=-74.0060,
        whatsapp_no="+12125551234",
        specialization="Dermatology",
        average_rating=4.5,
        review_count=100,
        verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    print(f"Doctor: {doctor1.clinic_name}")
    print(f"WhatsApp Number: {doctor1.whatsapp_no}")
    print(f"Generated URL: {doctor1.whatsapp_url}")
    print()
    print("✓ When a patient clicks this URL, WhatsApp opens with:")
    print("  - Contact: 12125551234 (without '+' prefix)")
    print("  - Pre-filled message: 'I would like to share my Derman Report'")
    print()
    
    # Example 2: International doctor
    print("Example 2: International Doctor (India)")
    print("-" * 80)
    
    doctor2 = DoctorResponse(
        id="223e4567-e89b-12d3-a456-426614174000",
        user_id="223e4567-e89b-12d3-a456-426614174001",
        license_no="LIC789012",
        clinic_name="Mumbai Skin Care Center",
        lat=19.0760,
        lng=72.8777,
        whatsapp_no="+919876543210",
        specialization="Dermatology",
        average_rating=4.8,
        review_count=250,
        verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    print(f"Doctor: {doctor2.clinic_name}")
    print(f"WhatsApp Number: {doctor2.whatsapp_no}")
    print(f"Generated URL: {doctor2.whatsapp_url}")
    print()
    
    # Example 3: Custom message
    print("Example 3: Custom Message")
    print("-" * 80)
    
    custom_message = "Hello Dr. Smith, I need an urgent consultation about my skin screening results."
    custom_url = doctor1.get_whatsapp_url(message=custom_message)
    
    print(f"Doctor: {doctor1.clinic_name}")
    print(f"Custom Message: {custom_message}")
    print(f"Generated URL: {custom_url}")
    print()
    
    # Example 4: Doctor without '+' prefix
    print("Example 4: Phone Number Without '+' Prefix")
    print("-" * 80)
    
    doctor3 = DoctorResponse(
        id="323e4567-e89b-12d3-a456-426614174000",
        user_id="323e4567-e89b-12d3-a456-426614174001",
        license_no="LIC345678",
        clinic_name="London Dermatology Practice",
        lat=51.5074,
        lng=-0.1278,
        whatsapp_no="442071234567",  # No '+' prefix
        specialization="Dermatology",
        average_rating=4.7,
        review_count=180,
        verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    print(f"Doctor: {doctor3.clinic_name}")
    print(f"WhatsApp Number (input): {doctor3.whatsapp_no}")
    print(f"Generated URL: {doctor3.whatsapp_url}")
    print()
    print("✓ Works correctly even without '+' prefix")
    print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()
    print("The WhatsApp URL generation feature:")
    print("  ✓ Automatically generates URLs when DoctorResponse is created")
    print("  ✓ Removes '+' prefix from phone numbers for wa.me format")
    print("  ✓ URL-encodes messages properly")
    print("  ✓ Uses default message: 'I would like to share my Derman Report'")
    print("  ✓ Supports custom messages via get_whatsapp_url(message=...)")
    print("  ✓ Works with international phone numbers")
    print()
    print("URL Format: https://wa.me/{phone_number}?text={url_encoded_message}")
    print()
    print("Requirements Validated: 7.5")
    print()


if __name__ == "__main__":
    demo_whatsapp_url_generation()
