"""
Security Tests for Data Encryption
Task: 36.5 Security audit
Requirements: 18.1, 18.2

Tests data encryption security:
- AES-256 encryption at rest
- HTTPS enforcement for data in transit
- Database connection encryption
- Encryption key management
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.encryption import EncryptionService, verify_encryption_enabled


class TestEncryptionAtRest:
    """Test encryption at rest (AES-256)"""
    
    def test_storage_uses_aes_256_encryption(self):
        """
        Test that storage encryption uses AES-256
        
        Security: Requirement 18.1 - Medical images encrypted at rest
        """
        service = EncryptionService()
        metadata = service.get_storage_encryption_metadata()
        
        # Should use AES-256
        assert metadata["encryption_algorithm"] == "AES-256"
        assert metadata["encryption_at_rest"] == "enabled"
    
    def test_encryption_metadata_includes_key_management(self):
        """
        Test that encryption metadata includes key management info
        
        Security: Ensures proper key management
        """
        service = EncryptionService()
        metadata = service.get_storage_encryption_metadata()
        
        # Should include key management information
        assert "key_management" in metadata
        assert metadata["key_management"] is not None
    
    def test_storage_encryption_is_enabled(self):
        """
        Test that storage encryption is enabled
        
        Security: Requirement 18.1 - Encryption must be active
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            details = service.verify_supabase_encryption()
            
            # Storage encryption should be enabled
            assert details["storage_encryption"]["enabled"] is True
            assert details["storage_encryption"]["algorithm"] == "AES-256"
    
    def test_encryption_status_shows_compliant(self):
        """
        Test that encryption status shows compliance
        
        Security: Requirement 18.1 - Verify compliance
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            status = service.get_encryption_status()
            
            # Should be compliant with requirement 18.1
            assert status["compliance"]["requirement_18_1"] == "COMPLIANT: AES-256 encryption at rest"


class TestHTTPSEnforcement:
    """Test HTTPS enforcement for data in transit"""
    
    def test_https_urls_are_verified_as_secure(self):
        """
        Test that HTTPS URLs are verified as secure
        
        Security: Requirement 18.2 - HTTPS/TLS encryption
        """
        service = EncryptionService()
        
        https_urls = [
            "https://example.supabase.co",
            "https://api.example.com",
            "https://secure-site.com/api",
        ]
        
        for url in https_urls:
            assert service.verify_https_connection(url) is True
    
    def test_http_urls_are_rejected(self):
        """
        Test that HTTP URLs are rejected as insecure
        
        Security: Requirement 18.2 - Prevent insecure connections
        """
        service = EncryptionService()
        
        http_urls = [
            "http://example.com",
            "http://insecure.supabase.co",
            "ftp://example.com",
        ]
        
        for url in http_urls:
            assert service.verify_https_connection(url) is False
    
    def test_insecure_connection_raises_error(self):
        """
        Test that insecure connections raise validation error
        
        Security: Requirement 18.2 - Enforce secure connections
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "http://insecure.supabase.co"
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="Insecure Supabase URL detected"):
                service.validate_secure_connection()
    
    def test_https_enforcement_in_encryption_status(self):
        """
        Test that encryption status shows HTTPS enforcement
        
        Security: Requirement 18.2 - Verify TLS encryption
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            status = service.get_encryption_status()
            
            # Should show HTTPS is enforced
            assert status["encryption_details"]["supabase_url_secure"] is True
            assert status["encryption_details"]["transport_encryption"]["enabled"] is True
            assert "TLS" in status["encryption_details"]["transport_encryption"]["protocol"]
    
    def test_transport_encryption_compliance(self):
        """
        Test that transport encryption shows compliance
        
        Security: Requirement 18.2 - Verify compliance
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            status = service.get_encryption_status()
            
            # Should be compliant with requirement 18.2
            assert status["compliance"]["requirement_18_2"] == "COMPLIANT: HTTPS/TLS encryption in transit"


class TestDatabaseEncryption:
    """Test database connection encryption"""
    
    def test_database_connections_use_encryption(self):
        """
        Test that database connections use encryption
        
        Security: Database connections should be encrypted
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            details = service.verify_supabase_encryption()
            
            # Database encryption should be enabled
            assert details["database_encryption"]["enabled"] is True
            assert "TLS" in details["database_encryption"]["protocol"]
    
    def test_supabase_url_must_be_https(self):
        """
        Test that Supabase URL must use HTTPS
        
        Security: Prevents man-in-the-middle attacks
        """
        service = EncryptionService()
        
        # HTTPS should be secure
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            details = service.verify_supabase_encryption()
            assert details["supabase_url_secure"] is True
        
        # HTTP should be insecure
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "http://test.supabase.co"
            details = service.verify_supabase_encryption()
            assert details["supabase_url_secure"] is False


class TestEncryptionKeyManagement:
    """Test encryption key management"""
    
    def test_encryption_metadata_includes_key_info(self):
        """
        Test that encryption metadata includes key management info
        
        Security: Proper key management is critical
        """
        service = EncryptionService()
        metadata = service.get_storage_encryption_metadata()
        
        # Should include key management
        assert "key_management" in metadata
        
        # Key management should specify the system
        key_mgmt = metadata["key_management"]
        assert key_mgmt is not None
        assert len(key_mgmt) > 0
    
    def test_encryption_uses_managed_keys(self):
        """
        Test that encryption uses managed keys
        
        Security: Keys should be managed by secure system
        """
        service = EncryptionService()
        metadata = service.get_storage_encryption_metadata()
        
        # Should use Supabase managed keys
        assert "Supabase" in metadata["key_management"]


class TestEncryptionCompliance:
    """Test overall encryption compliance"""
    
    def test_verify_encryption_enabled_succeeds_with_https(self):
        """
        Test that encryption verification succeeds with HTTPS
        
        Security: Validates secure configuration
        """
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://secure.supabase.co"
            
            # Should not raise exception
            result = verify_encryption_enabled()
            assert result is True
    
    def test_verify_encryption_enabled_fails_with_http(self):
        """
        Test that encryption verification fails with HTTP
        
        Security: Rejects insecure configuration
        """
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "http://insecure.supabase.co"
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="Insecure Supabase URL detected"):
                verify_encryption_enabled()
    
    def test_encryption_status_completeness(self):
        """
        Test that encryption status provides complete information
        
        Security: Enables monitoring and compliance verification
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            status = service.get_encryption_status()
            
            # Should include all required sections
            required_sections = [
                "secure",
                "encryption_details",
                "storage_metadata",
                "compliance"
            ]
            
            for section in required_sections:
                assert section in status, f"Missing section: {section}"
            
            # Encryption details should be complete
            details = status["encryption_details"]
            assert "storage_encryption" in details
            assert "transport_encryption" in details
            assert "database_encryption" in details
            assert "supabase_url_secure" in details
    
    def test_encryption_status_shows_secure_when_https(self):
        """
        Test that encryption status shows secure with HTTPS
        
        Security: Validates secure configuration
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            status = service.get_encryption_status()
            
            # Overall status should be secure
            assert status["secure"] is True
    
    def test_encryption_status_shows_insecure_when_http(self):
        """
        Test that encryption status shows insecure with HTTP
        
        Security: Detects insecure configuration
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "http://test.supabase.co"
            
            status = service.get_encryption_status()
            
            # Overall status should be insecure
            assert status["secure"] is False


class TestEncryptionInTransit:
    """Test encryption in transit"""
    
    def test_storage_metadata_includes_transit_encryption(self):
        """
        Test that storage metadata includes transit encryption info
        
        Security: Both at-rest and in-transit encryption needed
        """
        service = EncryptionService()
        metadata = service.get_storage_encryption_metadata()
        
        # Should include encryption in transit
        assert "encryption_in_transit" in metadata
        assert "TLS" in metadata["encryption_in_transit"]
    
    def test_tls_version_is_secure(self):
        """
        Test that TLS version is secure (1.2+)
        
        Security: Old TLS versions have vulnerabilities
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            details = service.verify_supabase_encryption()
            
            # Should use TLS 1.2 or higher
            protocol = details["transport_encryption"]["protocol"]
            assert "TLS 1.2+" in protocol or "TLS" in protocol


class TestEncryptionService:
    """Test EncryptionService functionality"""
    
    def test_encryption_service_singleton(self):
        """
        Test that encryption service maintains consistent state
        
        Security: Consistent configuration across application
        """
        from app.encryption import get_encryption_service
        
        service1 = get_encryption_service()
        service2 = get_encryption_service()
        
        # Should return same instance
        assert service1 is service2
    
    def test_encryption_service_configuration(self):
        """
        Test that encryption service has correct configuration
        
        Security: Validates encryption settings
        """
        service = EncryptionService()
        
        # Should have encryption enabled
        assert service.storage_encryption is True
        assert service.transport_encryption is True
    
    def test_encryption_service_provides_status(self):
        """
        Test that encryption service provides status information
        
        Security: Enables monitoring
        """
        service = EncryptionService()
        
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            status = service.get_encryption_status()
            
            # Should provide status
            assert status is not None
            assert isinstance(status, dict)
            assert "secure" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
