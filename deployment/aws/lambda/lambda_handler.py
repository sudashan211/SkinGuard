"""
SkinGuard Backend - AWS Lambda Handler
Adapts FastAPI application for AWS Lambda using Mangum
"""

from mangum import Mangum
from backend.app.main import app

# Create Lambda handler
handler = Mangum(app, lifespan="off")

# Optional: Custom handler with additional logic
def custom_handler(event, context):
    """
    Custom Lambda handler with pre/post processing
    """
    # Pre-processing
    print(f"Lambda invoked: {event.get('requestContext', {}).get('requestId')}")
    
    # Call Mangum handler
    response = handler(event, context)
    
    # Post-processing
    # Add custom headers, logging, etc.
    
    return response
