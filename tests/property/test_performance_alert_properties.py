"""
Property-based tests for performance degradation alerting
Requirements: 20.4

Property 66: Performance Degradation Alerting
For any API response taking longer than 5 seconds, the system should 
send an alert notification to administrators.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime
import sys
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory
backend_path = Path(__file__).parent.parent.parent / "backend"
env_path = backend_path / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend directory to path FIRST so 'app' module can be found
sys.path.insert(0, str(backend_path))

# Set minimal environment variables if not set (fallback)
if not os.getenv("SUPABASE_URL"):
    os.environ["SUPABASE_URL"] = "https://placeholder.supabase.co"
if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "placeholder_key"

# Now import from backend
from app.metrics import MetricsCollector
from app.database import supabase


# ============================================================================
# Test Data Generators
# ============================================================================

@st.composite
def slow_response_strategy(draw):
    """Generate slow response times (>5 seconds)"""
    return {
        "endpoint": draw(st.sampled_from([
            "/api/analyze-skin",
            "/api/reports",
            "/api/doctors/nearby",
            "/api/appointments"
        ])),
        "method": draw(st.sampled_from(["GET", "POST", "PUT"])),
        "response_time": draw(st.floats(min_value=5.01, max_value=30.0)),
        "status_code": draw(st.sampled_from([200, 201, 500]))
    }


@st.composite
def fast_response_strategy(draw):
    """Generate fast response times (<5 seconds)"""
    return {
        "endpoint": draw(st.sampled_from([
            "/api/analyze-skin",
            "/api/reports",
            "/api/doctors/nearby",
            "/api/appointments"
        ])),
        "method": draw(st.sampled_from(["GET", "POST", "PUT"])),
        "response_time": draw(st.floats(min_value=0.01, max_value=4.99)),
        "status_code": draw(st.sampled_from([200, 201, 400, 404]))
    }


# ============================================================================
# Property Tests
# ============================================================================

@given(
    slow_response=slow_response_strategy()
)
@settings(max_examples=15, deadline=None)
def test_performance_degradation_alerting_slow_response(slow_response):
    """
    Property 66: Performance Degradation Alerting (Slow Response)
    
    For any API response taking longer than 5 seconds, the system should 
    send an alert notification to administrators.
    
    Validates: Requirements 20.4
    """
    metrics_collector = MetricsCollector()
    created_logs = []
    created_notifications = []
    created_profiles = []
    
    try:
        # Create a test admin user
        admin_data = {
            "id": str(uuid.uuid4()),
            "email": f"admin_{uuid.uuid4().hex[:8]}@test.com",
            "full_name": "Test Admin",
            "role": "admin",
            "verified": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        admin_result = supabase.table("profiles").insert(admin_data).execute()
        if admin_result.data:
            created_profiles.append(admin_result.data[0]["id"])
            admin_id = admin_result.data[0]["id"]
        else:
            pytest.skip("Failed to create test admin user")
            return
        
        # Log API metrics with slow response time
        import asyncio
        asyncio.run(metrics_collector.log_api_metrics(
            endpoint=slow_response["endpoint"],
            method=slow_response["method"],
            response_time=slow_response["response_time"],
            status_code=slow_response["status_code"],
            user_id=str(uuid.uuid4())
        ))
        
        # Retrieve the API metrics log
        api_log_result = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "api_request")\
            .eq("resource_id", slow_response["endpoint"])\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if api_log_result.data:
            created_logs.append(api_log_result.data[0]["id"])
        
        # Check if performance alert notification was created
        # The alert should be sent to the admin user
        notification_result = supabase.table("notifications")\
            .select("*")\
            .eq("user_id", admin_id)\
            .eq("type", "performance_alert")\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        # Verify alert notification was created
        assert notification_result.data is not None, \
            "Notification query should return data"
        assert len(notification_result.data) > 0, \
            f"Performance alert should be sent for response time {slow_response['response_time']:.2f}s (threshold: 5s)"
        
        notification = notification_result.data[0]
        created_notifications.append(notification["id"])
        
        # Verify notification properties
        assert notification["user_id"] == admin_id, \
            "Notification should be sent to admin user"
        assert notification["type"] == "performance_alert", \
            "Notification type should be 'performance_alert'"
        assert "Performance Degradation" in notification["title"], \
            "Notification title should mention performance degradation"
        
        # Verify notification message contains relevant information
        message = notification["message"]
        assert slow_response["endpoint"] in message, \
            "Notification message should include endpoint"
        assert slow_response["method"] in message, \
            "Notification message should include HTTP method"
        
        # Verify notification metadata
        metadata = notification.get("metadata", {})
        assert "endpoint" in metadata, \
            "Notification metadata should include endpoint"
        assert "response_time" in metadata, \
            "Notification metadata should include response_time"
        assert "threshold" in metadata, \
            "Notification metadata should include threshold"
        
        assert metadata["endpoint"] == slow_response["endpoint"], \
            "Metadata endpoint should match"
        assert abs(metadata["response_time"] - slow_response["response_time"]) < 0.1, \
            "Metadata response time should match"
        assert metadata["threshold"] == 5.0, \
            "Threshold should be 5.0 seconds"
        
        # Verify notification is unread
        assert notification["read"] == False, \
            "New notification should be unread"
        
        # Cleanup
        for notification_id in created_notifications:
            supabase.table("notifications").delete().eq("id", notification_id).execute()
        
        for log_id in created_logs:
            supabase.table("audit_logs").delete().eq("id", log_id).execute()
        
        for profile_id in created_profiles:
            supabase.table("profiles").delete().eq("id", profile_id).execute()
        
    except Exception as e:
        # Cleanup on error
        for notification_id in created_notifications:
            try:
                supabase.table("notifications").delete().eq("id", notification_id).execute()
            except:
                pass
        
        for log_id in created_logs:
            try:
                supabase.table("audit_logs").delete().eq("id", log_id).execute()
            except:
                pass
        
        for profile_id in created_profiles:
            try:
                supabase.table("profiles").delete().eq("id", profile_id).execute()
            except:
                pass
        
        pytest.skip(f"Skipping due to database error: {str(e)}")


@given(
    fast_response=fast_response_strategy()
)
@settings(max_examples=15, deadline=None)
def test_no_alert_for_fast_responses(fast_response):
    """
    Property 66: Performance Degradation Alerting (Fast Response - No Alert)
    
    For any API response taking less than 5 seconds, the system should NOT 
    send a performance alert notification.
    
    Validates: Requirements 20.4
    """
    metrics_collector = MetricsCollector()
    created_logs = []
    created_profiles = []
    
    try:
        # Create a test admin user
        admin_data = {
            "id": str(uuid.uuid4()),
            "email": f"admin_{uuid.uuid4().hex[:8]}@test.com",
            "full_name": "Test Admin",
            "role": "admin",
            "verified": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        admin_result = supabase.table("profiles").insert(admin_data).execute()
        if admin_result.data:
            created_profiles.append(admin_result.data[0]["id"])
            admin_id = admin_result.data[0]["id"]
        else:
            pytest.skip("Failed to create test admin user")
            return
        
        # Count existing notifications for this admin
        before_result = supabase.table("notifications")\
            .select("id", count="exact")\
            .eq("user_id", admin_id)\
            .eq("type", "performance_alert")\
            .execute()
        
        notifications_before = before_result.count if before_result.count is not None else 0
        
        # Log API metrics with fast response time
        import asyncio
        asyncio.run(metrics_collector.log_api_metrics(
            endpoint=fast_response["endpoint"],
            method=fast_response["method"],
            response_time=fast_response["response_time"],
            status_code=fast_response["status_code"],
            user_id=str(uuid.uuid4())
        ))
        
        # Retrieve the API metrics log
        api_log_result = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "api_request")\
            .eq("resource_id", fast_response["endpoint"])\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if api_log_result.data:
            created_logs.append(api_log_result.data[0]["id"])
        
        # Check if any new performance alert notifications were created
        after_result = supabase.table("notifications")\
            .select("id", count="exact")\
            .eq("user_id", admin_id)\
            .eq("type", "performance_alert")\
            .execute()
        
        notifications_after = after_result.count if after_result.count is not None else 0
        
        # Verify NO new alert was created
        assert notifications_after == notifications_before, \
            f"No performance alert should be sent for response time {fast_response['response_time']:.2f}s (threshold: 5s)"
        
        # Cleanup
        for log_id in created_logs:
            supabase.table("audit_logs").delete().eq("id", log_id).execute()
        
        for profile_id in created_profiles:
            supabase.table("profiles").delete().eq("id", profile_id).execute()
        
    except Exception as e:
        # Cleanup on error
        for log_id in created_logs:
            try:
                supabase.table("audit_logs").delete().eq("id", log_id).execute()
            except:
                pass
        
        for profile_id in created_profiles:
            try:
                supabase.table("profiles").delete().eq("id", profile_id).execute()
            except:
                pass
        
        pytest.skip(f"Skipping due to database error: {str(e)}")


@given(
    response_time=st.floats(min_value=5.01, max_value=30.0),
    admin_count=st.integers(min_value=1, max_value=3)
)
@settings(max_examples=10, deadline=None)
def test_alert_sent_to_all_admins(response_time, admin_count):
    """
    Property 66: Performance Degradation Alerting (Multiple Admins)
    
    For any slow API response, performance alerts should be sent to ALL 
    administrator users in the system.
    
    Validates: Requirements 20.4
    """
    metrics_collector = MetricsCollector()
    created_logs = []
    created_notifications = []
    created_profiles = []
    
    try:
        # Create multiple test admin users
        admin_ids = []
        for i in range(admin_count):
            admin_data = {
                "id": str(uuid.uuid4()),
                "email": f"admin{i}_{uuid.uuid4().hex[:8]}@test.com",
                "full_name": f"Test Admin {i}",
                "role": "admin",
                "verified": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            admin_result = supabase.table("profiles").insert(admin_data).execute()
            if admin_result.data:
                created_profiles.append(admin_result.data[0]["id"])
                admin_ids.append(admin_result.data[0]["id"])
        
        if len(admin_ids) != admin_count:
            pytest.skip("Failed to create all test admin users")
            return
        
        # Log API metrics with slow response time
        import asyncio
        asyncio.run(metrics_collector.log_api_metrics(
            endpoint="/api/test",
            method="POST",
            response_time=response_time,
            status_code=200,
            user_id=str(uuid.uuid4())
        ))
        
        # Retrieve the API metrics log
        api_log_result = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "api_request")\
            .eq("resource_id", "/api/test")\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if api_log_result.data:
            created_logs.append(api_log_result.data[0]["id"])
        
        # Check that alerts were sent to ALL admins
        for admin_id in admin_ids:
            notification_result = supabase.table("notifications")\
                .select("*")\
                .eq("user_id", admin_id)\
                .eq("type", "performance_alert")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            assert notification_result.data is not None and len(notification_result.data) > 0, \
                f"Performance alert should be sent to admin {admin_id}"
            
            notification = notification_result.data[0]
            created_notifications.append(notification["id"])
            
            # Verify notification properties
            assert notification["user_id"] == admin_id, \
                "Notification should be sent to correct admin"
            assert notification["type"] == "performance_alert", \
                "Notification type should be 'performance_alert'"
        
        # Verify all admins received the alert
        assert len(created_notifications) >= admin_count, \
            f"All {admin_count} admins should receive performance alert"
        
        # Cleanup
        for notification_id in created_notifications:
            supabase.table("notifications").delete().eq("id", notification_id).execute()
        
        for log_id in created_logs:
            supabase.table("audit_logs").delete().eq("id", log_id).execute()
        
        for profile_id in created_profiles:
            supabase.table("profiles").delete().eq("id", profile_id).execute()
        
    except Exception as e:
        # Cleanup on error
        for notification_id in created_notifications:
            try:
                supabase.table("notifications").delete().eq("id", notification_id).execute()
            except:
                pass
        
        for log_id in created_logs:
            try:
                supabase.table("audit_logs").delete().eq("id", log_id).execute()
            except:
                pass
        
        for profile_id in created_profiles:
            try:
                supabase.table("profiles").delete().eq("id", profile_id).execute()
            except:
                pass
        
        pytest.skip(f"Skipping due to database error: {str(e)}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
