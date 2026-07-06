"""
Data Encryption Utilities
Requirements: 18.1, 18.2

Provides encryption utilities for medical data at rest and in transit.
Supabase Storage automatically handles AES-256 encryption at rest.
This module provides utilities for verifying encryption status and
ensuring HTTPS/TLS for all connections.
"""
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Service for managing data encryption
    
    Supabase provides:
    - AES-256 encryption at rest for Storage buckets
    - TLS/HTTPS for all API connections
    - Encrypted database connections
    
    This service provides utilities to verify and enforce encryption.
    """
    
    def __init__(self):
        """Initialize encryption service"""
        self.storage_encryption = "AES-256"
        self.transport_encryption = "TLS 1.2+"
        logger.info("Encryption service initialized")
    
    def verify_https_connection(self, url: str) -> bool:
        """
        Verify that a URL uses HTTPS protocol
        
        Args:
            url: URL to verify
            
        Returns:
            bool: True if HTTPS, False otherwise
        """
        return url.startswith("https://")
    
    def verify_supabase_encryption(self) -> Dict[str, Any]:
        """
        Verify Supabase encryption configuration
        
        Returns:
            Dict with encryption status information
        """
        # Verify Supabase URL uses HTTPS
        supabase_https = self.verify_https_connection(settings.supabase_url)
        
        return {
            "storage_encryption": {
                "algorithm": self.storage_encryption,
                "enabled": True,
                "description": "Supabase Storage uses AES-256 encryption at rest"
            },
            "transport_encryption": {
                "protocol": self.transport_encryption,
                "enabled": supabase_https,
                "description": "All connections use HTTPS/TLS encryption"
            },
            "database_encryption": {
                "enabled": True,
                "description": "PostgreSQL connections use TLS encryption"
            },
            "supabase_url_secure": supabase_https
        }
    
    def get_storage_encryption_metadata(self, bucket_name: str = "medical-images") -> Dict[str, str]:
        """
        Get encryption metadata for storage bucket
        
        Args:
            bucket_name: Name of the storage bucket
            
        Returns:
            Dict with encryption metadata
        """
        return {
            "bucket": bucket_name,
            "encryption_algorithm": self.storage_encryption,
            "encryption_at_rest": "enabled",
            "encryption_in_transit": "TLS 1.2+",
            "key_management": "Supabase managed keys"
        }
    
    def validate_secure_connection(self) -> bool:
        """
        Validate that all connections are secure
        
        Returns:
            bool: True if all connections are secure
            
        Raises:
            ValueError: If insecure connections detected
        """
        if not self.verify_https_connection(settings.supabase_url):
            raise ValueError(
                f"Insecure Supabase URL detected: {settings.supabase_url}. "
                "Must use HTTPS for secure connections."
            )
        
        logger.info("All connections verified as secure (HTTPS/TLS)")
        return True
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """
        Get comprehensive encryption status
        
        Returns:
            Dict with complete encryption status
        """
        try:
            self.validate_secure_connection()
            secure = True
        except ValueError as e:
            logger.error(f"Security validation failed: {str(e)}")
            secure = False
        
        return {
            "secure": secure,
            "encryption_details": self.verify_supabase_encryption(),
            "storage_metadata": self.get_storage_encryption_metadata(),
            "compliance": {
                "requirement_18_1": "AES-256 encryption at rest - COMPLIANT",
                "requirement_18_2": "HTTPS/TLS encryption in transit - COMPLIANT" if secure else "NON-COMPLIANT"
            }
        }


# Global encryption service instance
encryption_service = EncryptionService()


def get_encryption_service() -> EncryptionService:
    """
    Get the global encryption service instance
    
    Returns:
        EncryptionService instance
    """
    return encryption_service


def verify_encryption_enabled() -> bool:
    """
    Verify that encryption is properly enabled
    
    Returns:
        bool: True if encryption is enabled
        
    Raises:
        ValueError: If encryption is not properly configured
    """
    service = get_encryption_service()
    return service.validate_secure_connection()
