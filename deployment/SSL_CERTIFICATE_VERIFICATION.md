# SSL/TLS Certificate Verification Procedures

## Overview

This document provides detailed procedures for verifying SSL/TLS certificates in the SkinGuard production environment. Proper SSL configuration is critical for protecting patient data and maintaining HIPAA compliance.

---

## 1. Pre-Installation Checklist

### 1.1 Certificate Requirements
- [ ] Certificate type: Domain Validated (DV) or Organization Validated (OV)
- [ ] Encryption: RSA 2048-bit or ECC 256-bit minimum
- [ ] Validity period: 1 year maximum (recommended: 90 days with auto-renewal)
- [ ] Subject Alternative Names (SANs) include all domains:
  - `skinguard.com`
  - `www.skinguard.com`
  - `api.skinguard.com`
  - `*.skinguard.com` (wildcard, if needed)

### 1.2 Certificate Authority (CA)
Recommended CAs:
- Let's Encrypt (free, 90-day certificates with auto-renewal)
- DigiCert
- Sectigo (formerly Comodo)
- GlobalSign

**Selection Criteria**:
- [ ] CA trusted by all major browsers
- [ ] CA supports automated renewal
- [ ] CA provides certificate transparency logs
- [ ] CA offers revocation checking (OCSP)

---

## 2. Certificate Installation

### 2.1 Let's Encrypt (Recommended)

#### Using Certbot (for Nginx/Apache)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate (Nginx)
sudo certbot --nginx -d skinguard.com -d www.skinguard.com -d api.skinguard.com

# Obtain certificate (Apache)
sudo certbot --apache -d skinguard.com -d www.skinguard.com -d api.skinguard.com

# Test auto-renewal
sudo certbot renew --dry-run
```

**Verification**:
```bash
# Check certificate files
ls -la /etc/letsencrypt/live/skinguard.com/
# Should see: cert.pem, chain.pem, fullchain.pem, privkey.pem

# Check certificate expiration
sudo certbot certificates
```

#### Using AWS Certificate Manager (for AWS services)

```bash
# Request certificate
aws acm request-certificate \
  --domain-name skinguard.com \
  --subject-alternative-names www.skinguard.com api.skinguard.com \
  --validation-method DNS \
  --region us-east-1

# Get validation records
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID

# Add CNAME records to DNS for validation
# Wait for validation to complete

# Check certificate status
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERT_ID \
  --query 'Certificate.Status'
```

### 2.2 Manual Certificate Installation

#### For Nginx

```nginx
# /etc/nginx/sites-available/skinguard.com

server {
    listen 443 ssl http2;
    server_name skinguard.com www.skinguard.com;

    # SSL Certificate
    ssl_certificate /etc/ssl/certs/skinguard.com.crt;
    ssl_certificate_key /etc/ssl/private/skinguard.com.key;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/certs/skinguard.com.chain.crt;

    # ... rest of configuration
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name skinguard.com www.skinguard.com;
    return 301 https://$server_name$request_uri;
}
```

**Apply Configuration**:
```bash
# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### For Apache

```apache
# /etc/apache2/sites-available/skinguard.com-ssl.conf

<VirtualHost *:443>
    ServerName skinguard.com
    ServerAlias www.skinguard.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/skinguard.com.crt
    SSLCertificateKeyFile /etc/ssl/private/skinguard.com.key
    SSLCertificateChainFile /etc/ssl/certs/skinguard.com.chain.crt

    # SSL Protocols and Ciphers
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder off

    # HSTS
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"

    # OCSP Stapling
    SSLUseStapling on
    SSLStaplingCache "shmcb:logs/ssl_stapling(32768)"

    # ... rest of configuration
</VirtualHost>

# HTTP to HTTPS redirect
<VirtualHost *:80>
    ServerName skinguard.com
    ServerAlias www.skinguard.com
    Redirect permanent / https://skinguard.com/
</VirtualHost>
```

**Apply Configuration**:
```bash
# Enable SSL module
sudo a2enmod ssl
sudo a2enmod headers

# Enable site
sudo a2ensite skinguard.com-ssl

# Test configuration
sudo apache2ctl configtest

# Reload Apache
sudo systemctl reload apache2
```

---

## 3. Certificate Verification

### 3.1 Basic Certificate Checks

#### Check Certificate Details
```bash
# View certificate details
openssl s_client -connect skinguard.com:443 -servername skinguard.com < /dev/null 2>/dev/null | openssl x509 -noout -text

# Check certificate expiration
echo | openssl s_client -servername skinguard.com -connect skinguard.com:443 2>/dev/null | openssl x509 -noout -dates

# Check certificate issuer
echo | openssl s_client -servername skinguard.com -connect skinguard.com:443 2>/dev/null | openssl x509 -noout -issuer

# Check certificate subject
echo | openssl s_client -servername skinguard.com -connect skinguard.com:443 2>/dev/null | openssl x509 -noout -subject

# Check Subject Alternative Names (SANs)
echo | openssl s_client -servername skinguard.com -connect skinguard.com:443 2>/dev/null | openssl x509 -noout -text | grep -A1 "Subject Alternative Name"
```

**Expected Output**:
```
notBefore=Dec 15 00:00:00 2024 GMT
notAfter=Mar 15 23:59:59 2025 GMT
issuer=C = US, O = Let's Encrypt, CN = R3
subject=CN = skinguard.com
DNS:skinguard.com, DNS:www.skinguard.com, DNS:api.skinguard.com
```

#### Verify Certificate Chain
```bash
# Check certificate chain
openssl s_client -connect skinguard.com:443 -servername skinguard.com -showcerts < /dev/null 2>/dev/null

# Verify certificate chain is complete
echo | openssl s_client -servername skinguard.com -connect skinguard.com:443 2>/dev/null | grep -E "Verify return code"
```

**Expected Output**:
```
Verify return code: 0 (ok)
```

**Common Error Codes**:
- `20`: Unable to get local issuer certificate (incomplete chain)
- `21`: Unable to verify the first certificate (missing intermediate)
- `10`: Certificate has expired

### 3.2 Browser Testing

#### Manual Browser Test
1. Open browser (Chrome, Firefox, Safari, Edge)
2. Navigate to `https://skinguard.com`
3. Click padlock icon in address bar
4. View certificate details

**Verification Checklist**:
- [ ] Padlock icon shows (no warnings)
- [ ] Certificate issued to correct domain
- [ ] Certificate not expired
- [ ] Certificate chain complete
- [ ] No mixed content warnings

#### Automated Browser Test
```bash
# Using curl
curl -I https://skinguard.com

# Check for HTTPS redirect
curl -I http://skinguard.com

# Verify HSTS header
curl -I https://skinguard.com | grep -i strict-transport-security
```

**Expected Output**:
```
HTTP/2 200
strict-transport-security: max-age=31536000; includeSubDomains; preload
```

### 3.3 SSL Labs Test

**Online Test**:
1. Visit: https://www.ssllabs.com/ssltest/
2. Enter domain: `skinguard.com`
3. Click "Submit"
4. Wait for scan to complete (2-5 minutes)

**Target Rating**: A or A+

**Verification Checklist**:
- [ ] Overall rating: A or A+
- [ ] Certificate: 100/100
- [ ] Protocol Support: 100/100 (TLS 1.2 and 1.3 only)
- [ ] Key Exchange: 90/100 or higher
- [ ] Cipher Strength: 90/100 or higher
- [ ] No vulnerabilities detected

**Common Issues and Fixes**:

| Issue | Fix |
|-------|-----|
| TLS 1.0/1.1 enabled | Disable in server config |
| Weak ciphers | Update cipher suite list |
| Missing HSTS | Add HSTS header |
| Certificate chain incomplete | Include intermediate certificates |
| Forward secrecy not supported | Enable ECDHE ciphers |

### 3.4 Protocol and Cipher Testing

#### Test TLS Versions
```bash
# Test TLS 1.0 (should fail)
openssl s_client -connect skinguard.com:443 -tls1 < /dev/null 2>&1 | grep -E "Protocol|Cipher"

# Test TLS 1.1 (should fail)
openssl s_client -connect skinguard.com:443 -tls1_1 < /dev/null 2>&1 | grep -E "Protocol|Cipher"

# Test TLS 1.2 (should succeed)
openssl s_client -connect skinguard.com:443 -tls1_2 < /dev/null 2>&1 | grep -E "Protocol|Cipher"

# Test TLS 1.3 (should succeed)
openssl s_client -connect skinguard.com:443 -tls1_3 < /dev/null 2>&1 | grep -E "Protocol|Cipher"
```

**Expected Results**:
- TLS 1.0: Connection refused or handshake failure
- TLS 1.1: Connection refused or handshake failure
- TLS 1.2: Connection successful
- TLS 1.3: Connection successful

#### Test Cipher Suites
```bash
# List supported ciphers
nmap --script ssl-enum-ciphers -p 443 skinguard.com

# Test specific cipher
openssl s_client -connect skinguard.com:443 -cipher 'ECDHE-RSA-AES128-GCM-SHA256' < /dev/null 2>&1 | grep "Cipher"
```

**Recommended Cipher Suites** (in order of preference):
1. `TLS_AES_128_GCM_SHA256` (TLS 1.3)
2. `TLS_AES_256_GCM_SHA384` (TLS 1.3)
3. `TLS_CHACHA20_POLY1305_SHA256` (TLS 1.3)
4. `ECDHE-ECDSA-AES128-GCM-SHA256` (TLS 1.2)
5. `ECDHE-RSA-AES128-GCM-SHA256` (TLS 1.2)
6. `ECDHE-ECDSA-AES256-GCM-SHA384` (TLS 1.2)
7. `ECDHE-RSA-AES256-GCM-SHA384` (TLS 1.2)

**Weak Ciphers to Disable**:
- Any cipher with `RC4`
- Any cipher with `MD5`
- Any cipher with `DES` or `3DES`
- Any cipher with `NULL`
- Any cipher without forward secrecy (non-ECDHE)

### 3.5 OCSP Stapling Verification

```bash
# Check OCSP stapling
openssl s_client -connect skinguard.com:443 -servername skinguard.com -status < /dev/null 2>&1 | grep -A 17 "OCSP Response"
```

**Expected Output**:
```
OCSP Response Status: successful (0x0)
Response Type: Basic OCSP Response
Cert Status: good
```

**Benefits of OCSP Stapling**:
- Faster certificate validation
- Improved privacy (no direct OCSP queries)
- Reduced load on CA's OCSP servers

### 3.6 Certificate Transparency (CT) Logs

```bash
# Check CT logs
curl -s "https://crt.sh/?q=skinguard.com&output=json" | jq '.[0]'
```

**Verification**:
- [ ] Certificate appears in CT logs
- [ ] Certificate logged within 24 hours of issuance
- [ ] No unauthorized certificates for domain

**CT Log Monitors**:
- https://crt.sh/
- https://transparencyreport.google.com/https/certificates

---

## 4. Security Headers Verification

### 4.1 HSTS (HTTP Strict Transport Security)

```bash
# Check HSTS header
curl -I https://skinguard.com | grep -i strict-transport-security
```

**Expected Header**:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Parameters**:
- `max-age=31536000`: 1 year (recommended)
- `includeSubDomains`: Apply to all subdomains
- `preload`: Eligible for browser preload list

**HSTS Preload Submission**:
1. Visit: https://hstspreload.org/
2. Enter domain: `skinguard.com`
3. Check eligibility
4. Submit for preload list (optional, but recommended)

### 4.2 Other Security Headers

```bash
# Check all security headers
curl -I https://skinguard.com
```

**Required Headers**:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 5. Mixed Content Detection

### 5.1 Manual Check

1. Open browser developer tools (F12)
2. Navigate to `https://skinguard.com`
3. Check Console tab for mixed content warnings

**Common Mixed Content Issues**:
- Images loaded over HTTP
- Scripts loaded over HTTP
- Stylesheets loaded over HTTP
- API calls to HTTP endpoints

### 5.2 Automated Check

```bash
# Using curl to check for HTTP resources
curl -s https://skinguard.com | grep -i 'http://'

# Using online tool
# Visit: https://www.whynopadlock.com/
# Enter: https://skinguard.com
```

**Fix**:
- Update all resource URLs to HTTPS
- Use protocol-relative URLs: `//example.com/resource.js`
- Use Content Security Policy to block mixed content

---

## 6. Certificate Renewal

### 6.1 Let's Encrypt Auto-Renewal

```bash
# Check renewal timer
sudo systemctl status certbot.timer

# Test renewal
sudo certbot renew --dry-run

# Force renewal (if needed)
sudo certbot renew --force-renewal

# Check renewal logs
sudo cat /var/log/letsencrypt/letsencrypt.log
```

**Renewal Schedule**:
- Let's Encrypt certificates expire after 90 days
- Certbot attempts renewal 30 days before expiration
- Renewal runs twice daily via systemd timer

### 6.2 Manual Renewal Reminder

**Set up monitoring**:
```bash
# Create script to check certificate expiration
cat > /usr/local/bin/check-cert-expiry.sh << 'EOF'
#!/bin/bash
DOMAIN="skinguard.com"
DAYS_WARNING=30

EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt $DAYS_WARNING ]; then
    echo "WARNING: Certificate for $DOMAIN expires in $DAYS_LEFT days!"
    # Send alert (email, Slack, etc.)
fi
EOF

chmod +x /usr/local/bin/check-cert-expiry.sh

# Add to crontab (run daily)
echo "0 9 * * * /usr/local/bin/check-cert-expiry.sh" | crontab -
```

### 6.3 Renewal Verification

After renewal:
```bash
# Check new certificate
sudo certbot certificates

# Verify new expiration date
echo | openssl s_client -servername skinguard.com -connect skinguard.com:443 2>/dev/null | openssl x509 -noout -dates

# Test HTTPS connection
curl -I https://skinguard.com

# Run SSL Labs test
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=skinguard.com
```

---

## 7. Troubleshooting

### 7.1 Common Issues

#### Issue: Certificate Not Trusted

**Symptoms**:
- Browser shows "Not Secure" warning
- `openssl` shows "Verify return code: 20"

**Causes**:
- Incomplete certificate chain
- Self-signed certificate
- Expired certificate

**Fix**:
```bash
# Check certificate chain
openssl s_client -connect skinguard.com:443 -servername skinguard.com -showcerts

# Ensure fullchain.pem is used (not just cert.pem)
# Nginx: ssl_certificate /etc/letsencrypt/live/skinguard.com/fullchain.pem;
# Apache: SSLCertificateChainFile /etc/letsencrypt/live/skinguard.com/chain.pem;
```

#### Issue: Certificate Name Mismatch

**Symptoms**:
- Browser shows "Certificate name mismatch" warning
- Accessing `www.skinguard.com` shows warning

**Causes**:
- Certificate doesn't include all domain names
- Missing Subject Alternative Names (SANs)

**Fix**:
```bash
# Reissue certificate with all domains
sudo certbot certonly --nginx -d skinguard.com -d www.skinguard.com -d api.skinguard.com
```

#### Issue: Mixed Content Warnings

**Symptoms**:
- Padlock icon shows warning
- Console shows "Mixed Content" errors

**Causes**:
- Resources loaded over HTTP

**Fix**:
```bash
# Find HTTP resources
grep -r "http://" /var/www/html/

# Update to HTTPS or protocol-relative URLs
sed -i 's|http://|https://|g' /var/www/html/index.html
```

#### Issue: HSTS Not Working

**Symptoms**:
- HSTS header not present
- Browser doesn't enforce HTTPS

**Causes**:
- Header not configured
- Header only sent on HTTPS (not HTTP)

**Fix**:
```nginx
# Nginx: Add to server block
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

```apache
# Apache: Add to VirtualHost
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
```

### 7.2 Certificate Revocation

If certificate is compromised:

```bash
# Revoke certificate (Let's Encrypt)
sudo certbot revoke --cert-path /etc/letsencrypt/live/skinguard.com/cert.pem

# Request new certificate
sudo certbot certonly --nginx -d skinguard.com -d www.skinguard.com -d api.skinguard.com

# Reload web server
sudo systemctl reload nginx
```

---

## 8. Monitoring and Alerts

### 8.1 Certificate Expiration Monitoring

**Tools**:
- SSL Labs: https://www.ssllabs.com/ssltest/
- Uptime Robot: https://uptimerobot.com/ (includes SSL monitoring)
- Pingdom: https://www.pingdom.com/
- StatusCake: https://www.statuscake.com/

**Setup Alert**:
```bash
# Using curl and cron
cat > /usr/local/bin/ssl-monitor.sh << 'EOF'
#!/bin/bash
DOMAIN="skinguard.com"
ALERT_DAYS=30
EMAIL="admin@skinguard.com"

EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt $ALERT_DAYS ]; then
    echo "SSL certificate for $DOMAIN expires in $DAYS_LEFT days" | mail -s "SSL Certificate Expiration Warning" $EMAIL
fi
EOF

chmod +x /usr/local/bin/ssl-monitor.sh

# Run daily at 9 AM
echo "0 9 * * * /usr/local/bin/ssl-monitor.sh" | crontab -
```

### 8.2 SSL Configuration Monitoring

**Periodic Checks** (monthly):
- [ ] Run SSL Labs test
- [ ] Check for new vulnerabilities (Heartbleed, POODLE, etc.)
- [ ] Review cipher suite recommendations
- [ ] Update TLS configuration if needed

---

## 9. Compliance Checklist

### 9.1 HIPAA Compliance
- [ ] TLS 1.2 or higher enabled
- [ ] Strong cipher suites only
- [ ] Certificate from trusted CA
- [ ] HSTS enabled
- [ ] No mixed content
- [ ] Certificate expiration monitoring
- [ ] Audit logging enabled

### 9.2 PCI DSS Compliance
- [ ] TLS 1.2 or higher (TLS 1.0/1.1 disabled)
- [ ] Strong cryptography (2048-bit RSA minimum)
- [ ] Certificate from trusted CA
- [ ] Regular vulnerability scans
- [ ] Certificate expiration monitoring

---

## 10. Verification Checklist

**Pre-Production**:
- [ ] Certificate installed correctly
- [ ] Certificate chain complete
- [ ] Certificate not expired
- [ ] All domains covered (SANs)
- [ ] TLS 1.2 and 1.3 enabled
- [ ] TLS 1.0 and 1.1 disabled
- [ ] Strong cipher suites configured
- [ ] Weak ciphers disabled
- [ ] HSTS header present
- [ ] OCSP stapling enabled
- [ ] HTTP to HTTPS redirect working
- [ ] No mixed content warnings
- [ ] SSL Labs rating: A or A+

**Post-Production**:
- [ ] Certificate expiration monitoring configured
- [ ] Auto-renewal configured (Let's Encrypt)
- [ ] Alert system tested
- [ ] Backup certificates stored securely
- [ ] Renewal procedure documented
- [ ] Team trained on renewal process

---

**Verified By**: _________________  
**Date**: _________________  
**SSL Labs Rating**: _________________  
**Certificate Expiration**: _________________
