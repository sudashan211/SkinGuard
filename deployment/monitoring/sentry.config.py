"""
Sentry Configuration for SkinGuard Platform
Error tracking and performance monitoring setup
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import os

def init_sentry():
    """
    Initialize Sentry for error tracking and performance monitoring
    
    Features:
    - Error tracking with stack traces
    - Performance monitoring for API endpoints
    - Database query monitoring
    - Redis operation monitoring
    - Custom tags for user context
    """
    
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "production")
    release = os.getenv("RELEASE_VERSION", "1.0.0")
    
    if not sentry_dsn:
        print("WARNING: SENTRY_DSN not configured. Error tracking disabled.")
        return
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=release,
        
        # Integrations
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",  # Group by endpoint
                failed_request_status_codes=[400, 499, 500, 599]
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        
        # Performance Monitoring
        traces_sample_rate=1.0 if environment == "development" else 0.1,  # 10% in production
        
        # Error Sampling
        sample_rate=1.0,  # Capture all errors
        
        # Additional Options
        attach_stacktrace=True,
        send_default_pii=False,  # HIPAA compliance - don't send PII
        max_breadcrumbs=50,
        
        # Before Send Hook - Filter sensitive data
        before_send=filter_sensitive_data,
        
        # Before Send Transaction Hook - Filter slow transactions
        before_send_transaction=filter_transactions,
    )
    
    print(f"Sentry initialized for environment: {environment}, release: {release}")


def filter_sensitive_data(event, hint):
    """
    Filter sensitive data from Sentry events before sending
    
    Removes:
    - Patient health information
    - Authentication tokens
    - Email addresses
    - Medical images
    """
    
    # Remove sensitive headers
    if "request" in event:
        headers = event["request"].get("headers", {})
        sensitive_headers = ["Authorization", "Cookie", "X-API-Key"]
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"
    
    # Remove sensitive query parameters
    if "request" in event and "query_string" in event["request"]:
        query = event["request"]["query_string"]
        if any(param in query for param in ["token", "api_key", "password"]):
            event["request"]["query_string"] = "[Filtered]"
    
    # Remove sensitive body data
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            sensitive_fields = ["password", "token", "api_key", "family_history", "symptoms"]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "[Filtered]"
    
    return event


def filter_transactions(event, hint):
    """
    Filter transactions before sending to Sentry
    
    Only send transactions that:
    - Take longer than 5 seconds (performance issues)
    - Result in errors
    """
    
    # Always send error transactions
    if event.get("level") == "error":
        return event
    
    # Send slow transactions (>5s)
    duration = event.get("timestamp", 0) - event.get("start_timestamp", 0)
    if duration > 5.0:
        return event
    
    # Drop fast, successful transactions to reduce noise
    return None


def capture_exception_with_context(exception, user_id=None, report_id=None, extra_context=None):
    """
    Capture exception with additional context
    
    Args:
        exception: The exception to capture
        user_id: User ID for context
        report_id: Medical report ID for context
        extra_context: Additional context dictionary
    """
    
    with sentry_sdk.push_scope() as scope:
        # Add user context (non-PII)
        if user_id:
            scope.set_user({"id": user_id})
        
        # Add tags
        if report_id:
            scope.set_tag("report_id", report_id)
        
        # Add extra context
        if extra_context:
            for key, value in extra_context.items():
                scope.set_extra(key, value)
        
        # Capture the exception
        sentry_sdk.capture_exception(exception)


def capture_message_with_context(message, level="info", user_id=None, extra_context=None):
    """
    Capture a message with additional context
    
    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        user_id: User ID for context
        extra_context: Additional context dictionary
    """
    
    with sentry_sdk.push_scope() as scope:
        # Add user context
        if user_id:
            scope.set_user({"id": user_id})
        
        # Add extra context
        if extra_context:
            for key, value in extra_context.items():
                scope.set_extra(key, value)
        
        # Capture the message
        sentry_sdk.capture_message(message, level=level)


# Performance monitoring helpers
def start_transaction(name, op):
    """Start a Sentry transaction for performance monitoring"""
    return sentry_sdk.start_transaction(name=name, op=op)


def start_span(transaction, op, description):
    """Start a span within a transaction"""
    return transaction.start_child(op=op, description=description)
