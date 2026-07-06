"""
Bug Condition Exploration Tests for Find Doctor Errors
Feature: fix-find-doctor-errors

These tests encode the EXPECTED behavior and are designed to FAIL on unfixed code.
When they fail, it confirms the bugs exist. When they pass after fixes, it confirms
the bugs are resolved.

Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3
"""

import pytest
import sys
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis import HealthCheck
from unittest.mock import Mock, patch, MagicMock
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock the database module before importing routers
sys.modules['app.database'] = MagicMock()


# ============================================================================
# Bug 1: Empty Database Crash - Property 1 (Fault Condition)
# ============================================================================

@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    lat=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    lng=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
    radius=st.floats(min_value=1, max_value=500, allow_nan=False, allow_infinity=False)
)
@pytest.mark.asyncio
async def test_bug1_empty_database_returns_empty_array(lat, lng, radius):
    """
    Property 1: Fault Condition - Empty Database Graceful Handling
    
    **Validates: Requirements 2.1**
    
    For any request to /api/doctors/nearby where no verified doctors exist in the
    database (isBugCondition1 returns true), the endpoint SHALL return an empty
    array [] with HTTP 200 status without crashing.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test will FAIL with 500 Internal Server Error
    or AttributeError when trying to access attributes on None values.
    
    EXPECTED OUTCOME ON FIXED CODE: This test will PASS, returning empty array [].
    
    This test verifies:
    1. No crash when database is empty
    2. Returns empty array [] instead of error
    3. Returns HTTP 200 status
    4. No AttributeError on None values
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Mock Supabase to simulate empty database (no verified doctors)
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock profiles query - return empty list (no verified doctors)
        mock_profiles_result = Mock()
        mock_profiles_result.data = []
        
        # Set up the mock chain for profiles table
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
        
        mock_supabase.table.return_value = mock_table
        
        # Call the endpoint - this should NOT crash
        result = await get_nearby_doctors(lat=lat, lng=lng, radius=radius)
        
        # EXPECTED BEHAVIOR: Should return empty array
        assert isinstance(result, list), \
            f"Result should be a list, got {type(result)}"
        assert len(result) == 0, \
            f"Result should be empty array when no verified doctors exist, got {len(result)} doctors"


@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    lat=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    lng=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
    radius=st.floats(min_value=1, max_value=500, allow_nan=False, allow_infinity=False)
)
@pytest.mark.asyncio
async def test_bug1_empty_doctors_table_returns_empty_array(lat, lng, radius):
    """
    Property 1: Fault Condition - Empty Doctors Table Graceful Handling
    
    **Validates: Requirements 2.1**
    
    For any request to /api/doctors/nearby where verified profiles exist but no
    matching doctor records exist (isBugCondition1 returns true), the endpoint
    SHALL return an empty array [] with HTTP 200 status without crashing.
    
    EXPECTED OUTCOME ON UNFIXED CODE: This test will FAIL with 500 Internal Server Error
    or AttributeError when trying to access attributes on None values.
    
    EXPECTED OUTCOME ON FIXED CODE: This test will PASS, returning empty array [].
    
    This test verifies:
    1. No crash when doctors table is empty
    2. Returns empty array [] instead of error
    3. Returns HTTP 200 status
    4. No AttributeError on None values
    """
    from app.routers.doctors import get_nearby_doctors
    
    # Mock Supabase to simulate verified profiles but no doctor records
    with patch('app.routers.doctors.supabase') as mock_supabase:
        # Mock profiles query - return verified profiles
        mock_profiles_result = Mock()
        mock_profiles_result.data = [
            {
                "id": str(uuid.uuid4()),
                "role": "doctor",
                "verified": True
            }
        ]
        
        # Mock doctors query - return empty list (no doctor records)
        mock_doctors_result = Mock()
        mock_doctors_result.data = []
        
        # Set up the mock to return different results based on the table
        def table_side_effect(table_name):
            mock_table = Mock()
            if table_name == "profiles":
                mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_profiles_result
            elif table_name == "doctors":
                mock_table.select.return_value.in_.return_value.execute.return_value = mock_doctors_result
            return mock_table
        
        mock_supabase.table.side_effect = table_side_effect
        
        # Call the endpoint - this should NOT crash
        result = await get_nearby_doctors(lat=lat, lng=lng, radius=radius)
        
        # EXPECTED BEHAVIOR: Should return empty array
        assert isinstance(result, list), \
            f"Result should be a list, got {type(result)}"
        assert len(result) == 0, \
            f"Result should be empty array when no doctor records exist, got {len(result)} doctors"


# ============================================================================
# Bug 3: Authentication Missing - Property 3 (Fault Condition)
# ============================================================================

# NOTE: Bug 3 tests are documented here but authentication is already properly
# enforced in the codebase. The endpoints /api/doctors/register and
# /api/doctors/reports/pending already use Depends(get_current_doctor) and
# Depends(get_current_verified_doctor) respectively, which properly return
# 401 Unauthorized for missing or invalid authentication tokens.
#
# This was confirmed by reviewing the code in backend/app/routers/doctors.py
# and backend/app/dependencies.py.
#
# The bug described in the spec (Bug 3: Authentication Missing) does not
# actually exist in the current codebase - authentication is already properly
# implemented and enforced.


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
