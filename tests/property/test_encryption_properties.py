"""
Property-Based Tests for Encryption
Feature: derman-ai-skin-screening

Tests encryption at rest and in transit.

Requirements: 18.1, 18.2
Properties: 51, 52
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.encryption import EncryptionService, get_encryption_service, verify_encryption_enabled


class TestEncryptionProperties:
    """Property-based tests for encryption features"""
    
    @given(
        bucket_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='-_'))
    )
    @settings(max_examples=100, deadline=None)
    def test_property_51_image_encryption_at_rest(self, bucket_name):
        """
        Property 51: Image Encryption at Rest
        
        For any stored medical image, the file metadata should indicate 
        AES-256 encryption is applied.
        
        Validates: Requirements 18.1
        
        This test verifies that:
        1. Storage encryption metadata indicates AES-256
        2. Encryption at rest is enabled
        3. Encryption metadata is consistent
        """
        # Arrange
        service = EncryptionService()
        
        # Act
        metadata = service.get_storage_encryption_metadata(bucket_name)
        
        # Assert - Verify AES-256 encryption is indicated
        assert metadata is not None, "Encryption metadata should not be None"
        assert "encryption_algorithm" in metadata, "Metadata should include encryption algorithm"
        assert metadata["encryption_algorithm"] == "AES-256", \
            f"Expected AES-256 encryption, got {metadata['encryption_algorithm']}"
        
        # Verify encryption at rest is enabled
        assert "encryption_at_rest" in metadata, "Metadata should include encryption_at_rest status"
        assert metadata["encryption_at_rest"] == "enabled", \
            f"Encryption at rest should be enabled, got {metadata['encryption_at_rest']}"
        
        # Verify bucket name is included
        assert metadata["bucket"] == bucket_name, \
            f"Bucket name mismatch: expected {bucket_name}, got {metadata['bucket']}"
        
        # Verify encryption in transit is specified
        assert "encryption_in_transit" in metadata, "Metadata should include encryption_in_transit"
        assert "TLS" in metadata["encryption_in_transit"], \
            "Encryption in transit should use TLS"
        
        # Verify key management is specified
        assert "key_management" in metadata, "Metadata should include key_management"
        assert metadata["key_management"] is not None, "Key management should be specified"
    
    @given(
        url=st.one_of(
            st.just("https://example.supabase.co"),
            st.just("https://test-project.supabase.co"),
            st.just("https://api.example.com"),
            st.builds(lambda domain: f"https://{domain}.supabase.co",
                     st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_52_https_transport_encryption_valid(self, url):
        """
        Property 52: HTTPS Transport Encryption (Valid URLs)
        
        For any client-server communication, the connection should use 
        HTTPS protocol with valid TLS certificate.
        
        Validates: Requirements 18.2
        
        This test verifies that:
        1. HTTPS URLs are correctly identified as secure
        2. Transport encryption is validated
        3. Secure connections are accepted
        """
        # Arrange
        service = EncryptionService()
        
        # Act
        is_https = service.verify_https_connection(url)
        
        # Assert - HTTPS URLs should be verified as secure
        assert is_https is True, f"HTTPS URL {url} should be verified as secure"
        
        # Verify encryption details
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = url
            
            encryption_details = service.verify_supabase_encryption()
            
            # Verify transport encryption is enabled
            assert encryption_details["transport_encryption"]["enabled"] is True, \
                "Transport encryption should be enabled for HTTPS URLs"
            
            # Verify protocol is TLS 1.2+
            assert "TLS" in encryption_details["transport_encryption"]["protocol"], \
                "Transport encryption should use TLS protocol"
            
            # Verify Supabase URL is secure
            assert encryption_details["supabase_url_secure"] is True, \
                "Supabase URL should be marked as secure"
    
    @given(
        url=st.one_of(
            st.just("http://example.com"),
            st.just("http://insecure.supabase.co"),
            st.just("ftp://example.com"),
            st.builds(lambda domain: f"http://{domain}.com",
                     st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_52_https_transport_encryption_invalid(self, url):
        """
        Property 52: HTTPS Transport Encryption (Invalid URLs)
        
        For any non-HTTPS URL, the connection should be rejected as insecure.
        
        Validates: Requirements 18.2
        
        This test verifies that:
        1. Non-HTTPS URLs are correctly identified as insecure
        2. Insecure connections are rejected
        3. Validation fails for HTTP/FTP protocols
        """
        # Arrange
        service = EncryptionService()
        
        # Act
        is_https = service.verify_https_connection(url)
        
        # Assert - Non-HTTPS URLs should be identified as insecure
        assert is_https is False, f"Non-HTTPS URL {url} should be identified as insecure"
        
        # Verify that validation fails for insecure URLs
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = url
            
            # Validation should fail
            with pytest.raises(ValueError, match="Insecure Supabase URL detected"):
                service.validate_secure_connection()
            
            # Encryption details should show transport encryption as disabled
            encryption_details = service.verify_supabase_encryption()
            assert encryption_details["transport_encryption"]["enabled"] is False, \
                "Transport encryption should be disabled for non-HTTPS URLs"
            
            assert encryption_details["supabase_url_secure"] is False, \
                "Supabase URL should be marked as insecure"
    
    def test_encryption_status_completeness(self):
        """
        Test that encryption status provides complete information
        
        Verifies that get_encryption_status returns all required fields
        for monitoring and compliance.
        """
        # Arrange
        service = EncryptionService()
        
        # Mock secure connection
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            # Act
            status = service.get_encryption_status()
            
            # Assert - Verify all required fields are present
            assert "secure" in status, "Status should include 'secure' field"
            assert "encryption_details" in status, "Status should include 'encryption_details'"
            assert "storage_metadata" in status, "Status should include 'storage_metadata'"
            assert "compliance" in status, "Status should include 'compliance'"
            
            # Verify encryption details structure
            details = status["encryption_details"]
            assert "storage_encryption" in details
            assert "transport_encryption" in details
            assert "database_encryption" in details
            assert "supabase_url_secure" in details
            
            # Verify storage metadata structure
            metadata = status["storage_metadata"]
            assert "bucket" in metadata
            assert "encryption_algorithm" in metadata
            assert "encryption_at_rest" in metadata
            assert "encryption_in_transit" in metadata
            
            # Verify compliance information
            compliance = status["compliance"]
            assert "requirement_18_1" in compliance
            assert "requirement_18_2" in compliance
            assert "COMPLIANT" in compliance["requirement_18_1"]
            assert "COMPLIANT" in compliance["requirement_18_2"]
    
    def test_encryption_service_singleton(self):
        """
        Test that encryption service maintains consistent state
        
        Verifies that get_encryption_service returns the same instance
        and maintains consistent configuration.
        """
        # Act
        service1 = get_encryption_service()
        service2 = get_encryption_service()
        
        # Assert - Should return same instance
        assert service1 is service2, "get_encryption_service should return singleton instance"
        
        # Verify consistent configuration
        assert service1.storage_encryption == service2.storage_encryption
        assert service1.transport_encryption == service2.transport_encryption
    
    def test_verify_encryption_enabled_success(self):
        """
        Test that verify_encryption_enabled succeeds with HTTPS
        
        Verifies that the verification function correctly validates
        secure connections.
        """
        # Arrange - Mock HTTPS Supabase URL
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://secure.supabase.co"
            
            # Act & Assert - Should not raise exception
            result = verify_encryption_enabled()
            assert result is True, "Verification should succeed for HTTPS URLs"
    
    def test_verify_encryption_enabled_failure(self):
        """
        Test that verify_encryption_enabled fails with HTTP
        
        Verifies that the verification function correctly rejects
        insecure connections.
        """
        # Arrange - Mock HTTP Supabase URL
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "http://insecure.supabase.co"
            
            # Act & Assert - Should raise ValueError
            with pytest.raises(ValueError, match="Insecure Supabase URL detected"):
                verify_encryption_enabled()
    
    @given(
        algorithm=st.sampled_from(["AES-256", "AES-128", "AES-192"])
    )
    @settings(max_examples=50, deadline=None)
    def test_storage_encryption_algorithm_consistency(self, algorithm):
        """
        Test that storage encryption algorithm is consistently reported
        
        Verifies that the encryption algorithm is always AES-256 as required.
        """
        # Arrange
        service = EncryptionService()
        
        # Act
        metadata = service.get_storage_encryption_metadata()
        
        # Assert - Should always be AES-256 regardless of input
        assert metadata["encryption_algorithm"] == "AES-256", \
            "Storage encryption must always use AES-256"
        
        # Verify in encryption details as well
        with patch('app.encryption.settings') as mock_settings:
            mock_settings.supabase_url = "https://test.supabase.co"
            
            details = service.verify_supabase_encryption()
            assert details["storage_encryption"]["algorithm"] == "AES-256", \
                "Encryption details must specify AES-256"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
