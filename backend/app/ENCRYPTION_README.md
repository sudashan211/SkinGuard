# Data Encryption Implementation

## Overview

SkinGuard implements comprehensive data encryption to protect sensitive medical information both at rest and in transit, meeting Requirements 18.1 and 18.2.

## Encryption at Rest (Requirement 18.1)

### Supabase Storage - AES-256 Encryption

All medical images stored in Supabase Storage are automatically encrypted at rest using **AES-256 encryption**.

**Configuration:**
- Bucket: `medical-images`
- Encryption Algorithm: AES-256
- Key Management: Supabase managed keys
- Automatic: Enabled by default in Supabase

**Verification:**
```bash
# Check encryption status
curl http://localhost:8000/api/encryption-status
```

**Database Configuration:**
The encryption is configured in `database/supabase_config.json`:
```json
{
  "storage": {
    "buckets": [
      {
        "name": "medical-images",
        "public": false,
        "encryption": "AES-256"
      }
    ]
  }
}
```

### Database Encryption

PostgreSQL data is encrypted at rest by Supabase:
- Database encryption: Enabled by default
- Connection encryption: TLS for all database connections
- Row Level Security (RLS): Enforced for data isolation

## Encryption in Transit (Requirement 18.2)

### HTTPS/TLS Encryption

All client-server communication uses HTTPS with TLS 1.2+ encryption.

**Requirements:**
- Supabase URL must use HTTPS protocol
- All API endpoints served over HTTPS
- TLS 1.2 or higher required

**Verification:**
The application verifies HTTPS connections on startup:
```python
from app.encryption import verify_encryption_enabled

# Raises ValueError if HTTPS not configured
verify_encryption_enabled()
```

**Production Deployment:**
- Use reverse proxy (nginx, Caddy) with TLS certificates
- Obtain certificates from Let's Encrypt or commercial CA
- Configure HSTS (HTTP Strict Transport Security)
- Disable HTTP, redirect all traffic to HTTPS

## Encryption Service

### Usage

```python
from app.encryption import get_encryption_service

# Get encryption service
service = get_encryption_service()

# Verify HTTPS connection
is_secure = service.verify_https_connection("https://example.com")

# Get encryption status
status = service.get_encryption_status()

# Validate all connections are secure
service.validate_secure_connection()

# Get storage encryption metadata
metadata = service.get_storage_encryption_metadata("medical-images")
```

### API Endpoints

#### GET /api/encryption-status

Returns comprehensive encryption status:

```json
{
  "timestamp": "2024-02-10T12:00:00Z",
  "secure": true,
  "encryption_details": {
    "storage_encryption": {
      "algorithm": "AES-256",
      "enabled": true,
      "description": "Supabase Storage uses AES-256 encryption at rest"
    },
    "transport_encryption": {
      "protocol": "TLS 1.2+",
      "enabled": true,
      "description": "All connections use HTTPS/TLS encryption"
    },
    "database_encryption": {
      "enabled": true,
      "description": "PostgreSQL connections use TLS encryption"
    },
    "supabase_url_secure": true
  },
  "storage_metadata": {
    "bucket": "medical-images",
    "encryption_algorithm": "AES-256",
    "encryption_at_rest": "enabled",
    "encryption_in_transit": "TLS 1.2+",
    "key_management": "Supabase managed keys"
  },
  "compliance": {
    "requirement_18_1": "AES-256 encryption at rest - COMPLIANT",
    "requirement_18_2": "HTTPS/TLS encryption in transit - COMPLIANT"
  }
}
```

## Security Best Practices

### Development Environment

For local development, you can use HTTP for the backend API, but Supabase connections should always use HTTPS:

```env
# .env
SUPABASE_URL=https://your-project.supabase.co  # Always HTTPS
```

### Production Environment

**Required:**
1. **TLS Certificate**: Obtain valid TLS certificate
2. **HTTPS Only**: Disable HTTP, use HTTPS exclusively
3. **HSTS**: Enable HTTP Strict Transport Security
4. **Certificate Renewal**: Automate certificate renewal (Let's Encrypt)

**Nginx Configuration Example:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.skinguard.com;
    
    ssl_certificate /etc/letsencrypt/live/api.skinguard.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.skinguard.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.skinguard.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring

### Startup Verification

The application automatically verifies encryption on startup:
- Checks Supabase URL uses HTTPS
- Validates secure connection configuration
- Logs warnings if encryption issues detected

### Runtime Monitoring

Monitor encryption status:
```bash
# Check encryption status
curl https://api.skinguard.com/api/encryption-status

# Check health
curl https://api.skinguard.com/api/health
```

### Logging

Encryption-related events are logged:
- Startup encryption verification
- Connection security validation
- Encryption status checks

## Compliance

### Requirement 18.1: Data Encryption at Rest
✅ **COMPLIANT**
- Medical images encrypted with AES-256 in Supabase Storage
- Database encrypted at rest by Supabase
- Automatic encryption, no manual configuration required

### Requirement 18.2: Transport Encryption
✅ **COMPLIANT**
- All connections use HTTPS/TLS
- Supabase connections always encrypted
- API served over HTTPS in production
- TLS 1.2+ required

## Troubleshooting

### Issue: "Insecure Supabase URL detected"

**Cause:** SUPABASE_URL in .env uses HTTP instead of HTTPS

**Solution:**
```env
# Wrong
SUPABASE_URL=http://your-project.supabase.co

# Correct
SUPABASE_URL=https://your-project.supabase.co
```

### Issue: Certificate errors in production

**Cause:** Invalid or expired TLS certificate

**Solution:**
1. Verify certificate is valid: `openssl s_client -connect api.skinguard.com:443`
2. Renew certificate: `certbot renew`
3. Restart web server: `systemctl restart nginx`

### Issue: Mixed content warnings

**Cause:** Loading HTTP resources from HTTPS page

**Solution:**
- Ensure all resources (images, scripts, API calls) use HTTPS
- Configure Content Security Policy (CSP) to block HTTP

## References

- Requirements: 18.1 (AES-256 encryption), 18.2 (HTTPS/TLS)
- Design Document: `.kiro/specs/derman-ai-skin-screening/design.md`
- Supabase Storage Docs: https://supabase.com/docs/guides/storage
- Supabase Security: https://supabase.com/docs/guides/platform/security
