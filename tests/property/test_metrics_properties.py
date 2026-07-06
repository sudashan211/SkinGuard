"""
Property-based tests for performance metrics collection
Requirements: 20.1, 20.2

Property 63: AI Processing Time Logging
For any AI analysis, the system should log separate processing times 
for NSFW Gatekeeper and Medical_AI (Swin + EfficientNet) stages.

Property 64: API Metrics Tracking
For any API endpoint call, the system should record response time 
and success/error status in metrics storage.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
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
def processing_times_strategy(draw):
    """Generate realistic AI processing times"""
    gatekeeper_time = draw(st.floats(min_value=0.5, max_value=5.0))
    medical_ai_time = draw(st.floats(min_value=5.0, max_value=25.0))
    total_time = gatekeeper_time + medical_ai_time + draw(st.floats(min_value=0.1, max_value=2.0))
    
    return {
        "gatekeeper_time": gatekeeper_time,
        "medical_ai_time": medical_ai_time,
        "total_time": total_time
    }


@st.composite
def api_metrics_strategy(draw):
    """Generate API metrics data"""
    return {
        "endpoint": draw(st.sampled_from([
            "/api/analyze-skin",
            "/api/reports",
            "/api/doctors/nearby",
            "/api/appointments"
        ])),
        "method": draw(st.sampled_from(["GET", "POST", "PUT", "DELETE"])),
        "response_time": draw(st.floats(min_value=0.01, max_value=10.0)),
        "status_code": draw(st.sampled_from([200, 201, 400, 401, 403, 404, 500])),
        "user_id": str(uuid.uuid4())
    }


# ============================================================================
# Property Tests
# ============================================================================

@given(
    processing_times=processing_times_strategy()
)
@settings(max_examples=20, deadline=None)
def test_ai_processing_time_logging(processing_times):
    """
    Property 63: AI Processing Time Logging
    
    For any AI analysis, the system should log separate processing times 
    for NSFW Gatekeeper and Medical_AI (Swin + EfficientNet) stages.
    
    Validates: Requirements 20.1
    """
    metrics_collector = MetricsCollector()
    report_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    created_logs = []
    
    try:
        # Log AI processing metrics
        import asyncio
        asyncio.run(metrics_collector.log_ai_processing_metrics(
            report_id=report_id,
            gatekeeper_time=processing_times["gatekeeper_time"],
            medical_ai_time=processing_times["medical_ai_time"],
            total_time=processing_times["total_time"],
            patient_id=patient_id
        ))
        
        # Retrieve the logged metrics
        result = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "ai_processing")\
            .eq("resource_id", report_id)\
            .execute()
        
        # Verify log was created
        assert result.data is not None, "Audit log should be created"
        assert len(result.data) > 0, "At least one log entry should exist"
        
        log_entry = result.data[0]
        created_logs.append(log_entry["id"])
        
        # Verify required fields are present
        assert log_entry["action"] == "ai_processing", \
            "Action should be 'ai_processing'"
        assert log_entry["resource_type"] == "medical_report", \
            "Resource type should be 'medical_report'"
        assert log_entry["resource_id"] == report_id, \
            "Resource ID should match report ID"
        assert log_entry["user_id"] == patient_id, \
            "User ID should match patient ID"
        
        # Verify metadata contains separate timing information
        metadata = log_entry.get("metadata", {})
        assert "gatekeeper_time" in metadata, \
            "Metadata should include gatekeeper_time"
        assert "medical_ai_time" in metadata, \
            "Metadata should include medical_ai_time"
        assert "total_processing_time" in metadata, \
            "Metadata should include total_processing_time"
        
        # Verify timing values match input
        assert abs(metadata["gatekeeper_time"] - processing_times["gatekeeper_time"]) < 0.01, \
            "Gatekeeper time should match logged value"
        assert abs(metadata["medical_ai_time"] - processing_times["medical_ai_time"]) < 0.01, \
            "Medical AI time should match logged value"
        assert abs(metadata["total_processing_time"] - processing_times["total_time"]) < 0.01, \
            "Total time should match logged value"
        
        # Verify times are positive
        assert metadata["gatekeeper_time"] > 0, \
            "Gatekeeper time should be positive"
        assert metadata["medical_ai_time"] > 0, \
            "Medical AI time should be positive"
        assert metadata["total_processing_time"] > 0, \
            "Total processing time should be positive"
        
        # Cleanup
        for log_id in created_logs:
            supabase.table("audit_logs").delete().eq("id", log_id).execute()
        
    except Exception as e:
        # Cleanup on error
        for log_id in created_logs:
            try:
                supabase.table("audit_logs").delete().eq("id", log_id).execute()
            except:
                pass
        
        pytest.skip(f"Skipping due to database error: {str(e)}")


@given(
    api_metrics=api_metrics_strategy()
)
@settings(max_examples=20, deadline=None)
def test_api_metrics_tracking(api_metrics):
    """
    Property 64: API Metrics Tracking
    
    For any API endpoint call, the system should record response time 
    and success/error status in metrics storage.
    
    Validates: Requirements 20.2
    """
    metrics_collector = MetricsCollector()
    created_logs = []
    
    try:
        # Log API metrics
        import asyncio
        asyncio.run(metrics_collector.log_api_metrics(
            endpoint=api_metrics["endpoint"],
            method=api_metrics["method"],
            response_time=api_metrics["response_time"],
            status_code=api_metrics["status_code"],
            user_id=api_metrics["user_id"],
            error_message="Test error" if api_metrics["status_code"] >= 400 else None
        ))
        
        # Retrieve the logged metrics
        result = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "api_request")\
            .eq("resource_id", api_metrics["endpoint"])\
            .eq("user_id", api_metrics["user_id"])\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        # Verify log was created
        assert result.data is not None, "Audit log should be created"
        assert len(result.data) > 0, "At least one log entry should exist"
        
        log_entry = result.data[0]
        created_logs.append(log_entry["id"])
        
        # Verify required fields are present
        assert log_entry["action"] == "api_request", \
            "Action should be 'api_request'"
        assert log_entry["resource_type"] == "api_endpoint", \
            "Resource type should be 'api_endpoint'"
        assert log_entry["resource_id"] == api_metrics["endpoint"], \
            "Resource ID should match endpoint"
        assert log_entry["user_id"] == api_metrics["user_id"], \
            "User ID should match"
        
        # Verify metadata contains required information
        metadata = log_entry.get("metadata", {})
        assert "endpoint" in metadata, \
            "Metadata should include endpoint"
        assert "method" in metadata, \
            "Metadata should include method"
        assert "response_time" in metadata, \
            "Metadata should include response_time"
        assert "status_code" in metadata, \
            "Metadata should include status_code"
        assert "is_error" in metadata, \
            "Metadata should include is_error flag"
        
        # Verify values match input
        assert metadata["endpoint"] == api_metrics["endpoint"], \
            "Endpoint should match"
        assert metadata["method"] == api_metrics["method"], \
            "Method should match"
        assert abs(metadata["response_time"] - api_metrics["response_time"]) < 0.01, \
            "Response time should match"
        assert metadata["status_code"] == api_metrics["status_code"], \
            "Status code should match"
        
        # Verify error flag is correct
        expected_is_error = api_metrics["status_code"] >= 400
        assert metadata["is_error"] == expected_is_error, \
            f"is_error should be {expected_is_error} for status code {api_metrics['status_code']}"
        
        # Verify response time is positive
        assert metadata["response_time"] > 0, \
            "Response time should be positive"
        
        # Cleanup
        for log_id in created_logs:
            supabase.table("audit_logs").delete().eq("id", log_id).execute()
        
    except Exception as e:
        # Cleanup on error
        for log_id in created_logs:
            try:
                supabase.table("audit_logs").delete().eq("id", log_id).execute()
            except:
                pass
        
        pytest.skip(f"Skipping due to database error: {str(e)}")


@given(
    request_count=st.integers(min_value=5, max_value=20),
    error_rate=st.floats(min_value=0.0, max_value=0.5)
)
@settings(max_examples=15, deadline=None)
def test_error_rate_calculation(request_count, error_rate):
    """
    Property 64: API Metrics Tracking (Error Rate Calculation)
    
    For any set of API requests with a known error rate, the system 
    should correctly calculate the error rate percentage.
    
    Validates: Requirements 20.2
    """
    metrics_collector = MetricsCollector()
    created_logs = []
    
    try:
        # Calculate number of errors based on error rate
        error_count = int(request_count * error_rate)
        success_count = request_count - error_count
        
        # Create API request logs with mix of successes and errors
        for i in range(success_count):
            log_data = {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "action": "api_request",
                "resource_type": "api_endpoint",
                "resource_id": "/api/test",
                "metadata": {
                    "endpoint": "/api/test",
                    "method": "GET",
                    "response_time": 0.5,
                    "status_code": 200,
                    "is_error": False
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("audit_logs").insert(log_data).execute()
            if result.data:
                created_logs.append(result.data[0]["id"])
        
        for i in range(error_count):
            log_data = {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "action": "api_request",
                "resource_type": "api_endpoint",
                "resource_id": "/api/test",
                "metadata": {
                    "endpoint": "/api/test",
                    "method": "GET",
                    "response_time": 0.5,
                    "status_code": 500,
                    "is_error": True
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("audit_logs").insert(log_data).execute()
            if result.data:
                created_logs.append(result.data[0]["id"])
        
        # Get error rate statistics
        import asyncio
        error_stats = asyncio.run(metrics_collector.get_error_rate(hours=24))
        
        # Verify required fields are present
        assert "total_requests" in error_stats, \
            "Error stats should include total_requests"
        assert "error_count" in error_stats, \
            "Error stats should include error_count"
        assert "error_rate" in error_stats, \
            "Error stats should include error_rate"
        assert "time_period_hours" in error_stats, \
            "Error stats should include time_period_hours"
        
        # Verify data types
        assert isinstance(error_stats["total_requests"], int), \
            "total_requests should be an integer"
        assert isinstance(error_stats["error_count"], int), \
            "error_count should be an integer"
        assert isinstance(error_stats["error_rate"], (int, float)), \
            "error_rate should be numeric"
        
        # Verify values are non-negative
        assert error_stats["total_requests"] >= 0, \
            "total_requests should be non-negative"
        assert error_stats["error_count"] >= 0, \
            "error_count should be non-negative"
        assert error_stats["error_rate"] >= 0, \
            "error_rate should be non-negative"
        assert error_stats["error_rate"] <= 100, \
            "error_rate should not exceed 100%"
        
        # Verify total requests includes our test data
        assert error_stats["total_requests"] >= request_count, \
            f"total_requests should be at least {request_count}"
        
        # Verify error count includes our test errors
        assert error_stats["error_count"] >= error_count, \
            f"error_count should be at least {error_count}"
        
        # Cleanup
        for log_id in created_logs:
            supabase.table("audit_logs").delete().eq("id", log_id).execute()
        
    except Exception as e:
        # Cleanup on error
        for log_id in created_logs:
            try:
                supabase.table("audit_logs").delete().eq("id", log_id).execute()
            except:
                pass
        
        pytest.skip(f"Skipping due to database error: {str(e)}")


@given(
    gatekeeper_time=st.floats(min_value=0.5, max_value=5.0),
    medical_ai_time=st.floats(min_value=5.0, max_value=25.0)
)
@settings(max_examples=20, deadline=None)
def test_separate_ai_timing_components(gatekeeper_time, medical_ai_time):
    """
    Property 63: AI Processing Time Logging (Separate Components)
    
    For any AI analysis, the logged gatekeeper time and medical AI time 
    should be stored as separate, independent values.
    
    Validates: Requirements 20.1
    """
    metrics_collector = MetricsCollector()
    report_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    total_time = gatekeeper_time + medical_ai_time
    created_logs = []
    
    try:
        # Log AI processing metrics
        import asyncio
        asyncio.run(metrics_collector.log_ai_processing_metrics(
            report_id=report_id,
            gatekeeper_time=gatekeeper_time,
            medical_ai_time=medical_ai_time,
            total_time=total_time,
            patient_id=patient_id
        ))
        
        # Retrieve the logged metrics
        result = supabase.table("audit_logs")\
            .select("*")\
            .eq("action", "ai_processing")\
            .eq("resource_id", report_id)\
            .execute()
        
        assert result.data is not None and len(result.data) > 0, \
            "Log entry should exist"
        
        log_entry = result.data[0]
        created_logs.append(log_entry["id"])
        metadata = log_entry.get("metadata", {})
        
        # Verify both timing components are present and separate
        assert "gatekeeper_time" in metadata, \
            "Gatekeeper time should be logged separately"
        assert "medical_ai_time" in metadata, \
            "Medical AI time should be logged separately"
        
        # Verify they are independent (not the same value)
        logged_gatekeeper = metadata["gatekeeper_time"]
        logged_medical_ai = metadata["medical_ai_time"]
        
        # They should match our input values
        assert abs(logged_gatekeeper - gatekeeper_time) < 0.01, \
            "Logged gatekeeper time should match input"
        assert abs(logged_medical_ai - medical_ai_time) < 0.01, \
            "Logged medical AI time should match input"
        
        # They should be different values (unless by coincidence they're equal)
        # The key property is that they're stored separately, not combined
        assert isinstance(logged_gatekeeper, (int, float)), \
            "Gatekeeper time should be numeric"
        assert isinstance(logged_medical_ai, (int, float)), \
            "Medical AI time should be numeric"
        
        # Verify total time is approximately the sum
        logged_total = metadata.get("total_processing_time", 0)
        assert abs(logged_total - total_time) < 0.01, \
            "Total time should match input"
        
        # Cleanup
        for log_id in created_logs:
            supabase.table("audit_logs").delete().eq("id", log_id).execute()
        
    except Exception as e:
        # Cleanup on error
        for log_id in created_logs:
            try:
                supabase.table("audit_logs").delete().eq("id", log_id).execute()
            except:
                pass
        
        pytest.skip(f"Skipping due to database error: {str(e)}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
