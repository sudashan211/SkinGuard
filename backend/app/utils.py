"""
Utility functions for SkinGuard platform
"""
from urllib.parse import quote


def generate_whatsapp_url(whatsapp_no: str, message: str = "I would like to share my Derman Report") -> str:
    """
    Generate WhatsApp contact URL with pre-filled message
    
    Requirements: 7.5
    
    Creates a WhatsApp URL in the format:
    https://wa.me/{whatsapp_no}?text={encoded_message}
    
    Args:
        whatsapp_no: Doctor's WhatsApp number (with country code, e.g., +15551234567)
        message: Pre-filled message text (default: "I would like to share my Derman Report")
        
    Returns:
        str: WhatsApp URL with encoded message
        
    Example:
        >>> generate_whatsapp_url("+15551234567")
        'https://wa.me/15551234567?text=I%20would%20like%20to%20share%20my%20Derman%20Report'
        
        >>> generate_whatsapp_url("+15551234567", "Hello Doctor")
        'https://wa.me/15551234567?text=Hello%20Doctor'
    """
    # Remove '+' prefix if present (WhatsApp API doesn't use it in URL)
    clean_number = whatsapp_no.lstrip('+')
    
    # URL encode the message
    encoded_message = quote(message)
    
    # Construct WhatsApp URL
    whatsapp_url = f"https://wa.me/{clean_number}?text={encoded_message}"
    
    return whatsapp_url
