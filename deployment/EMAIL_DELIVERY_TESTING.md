# Email Delivery Testing Procedures

## Overview

This document provides comprehensive procedures for testing email delivery in the SkinGuard production environment. Email is critical for user notifications, appointment confirmations, and emergency alerts.

---

## 1. Email Service Configuration

### 1.1 SendGrid Configuration

#### API Key Setup
```bash
# Set environment variable
export SENDGRID_API_KEY="SG.xxxxxxxxxxxxxxxxxxxxx"

# Test API key
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{
      "to": [{"email": "test@example.com"}]
    }],
    "from": {"email": "noreply@skinguard.com"},
    "subject": "Test Email",
    "content": [{
      "type": "text/plain",
      "value": "This is a test email"
    }]
  }'
```

**Expected Response**: HTTP 202 Accepted

#### Domain Authentication
```bash
# Verify domain authentication status
curl -X GET https://api.sendgrid.com/v3/whitelabel/domains \
  -H "Authorization: Bearer $SENDGRID_API_KEY"
```

**Verification Checklist**:
- [ ] Domain verified: `skinguard.com`
- [ ] SPF record configured
- [ ] DKIM keys configured
- [ ] DMARC policy configured
- [ ] Return path configured

**DNS Records to Verify**:
```bash
# Check SPF record
dig TXT skinguard.com | grep "v=spf1"

# Check DKIM record
dig TXT s1._domainkey.skinguard.com

# Check DMARC record
dig TXT _dmarc.skinguard.com
```

**Expected DNS Records**:
```
skinguard.com. IN TXT "v=spf1 include:sendgrid.net ~all"
s1._domainkey.skinguard.com. IN CNAME s1.domainkey.u12345.wl.sendgrid.net.
_dmarc.skinguard.com. IN TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@skinguard.com"
```

### 1.2 AWS SES Configuration (Alternative)

#### Verify Domain
```bash
# Verify domain
aws ses verify-domain-identity --domain skinguard.com

# Check verification status
aws ses get-identity-verification-attributes --identities skinguard.com

# Verify email address (for testing)
aws ses verify-email-identity --email-address noreply@skinguard.com
```

#### Configure DKIM
```bash
# Enable DKIM
aws ses set-identity-dkim-enabled --identity skinguard.com --dkim-enabled

# Get DKIM tokens
aws ses get-identity-dkim-attributes --identities skinguard.com
```

#### Move Out of Sandbox
```bash
# Check sending limits
aws ses get-send-quota

# Request production access (if in sandbox)
# Visit: https://console.aws.amazon.com/ses/home#/account
# Click "Request Production Access"
```

**Verification Checklist**:
- [ ] Domain verified
- [ ] DKIM enabled
- [ ] Out of sandbox mode
- [ ] Sending limits sufficient (50,000+ emails/day)
- [ ] Bounce and complaint notifications configured

---

## 2. Email Template Testing

### 2.1 Template Validation

#### Test All Email Templates
```bash
# List of email templates to test
TEMPLATES=(
  "welcome"
  "analysis_complete"
  "appointment_confirmation"
  "appointment_reminder"
  "doctor_verification"
  "follow_up_reminder"
  "urgent_case_alert"
)

# Test each template
for template in "${TEMPLATES[@]}"; do
  echo "Testing template: $template"
  curl -X POST https://api.skinguard.com/api/test/email/$template \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"recipient": "test@example.com"}'
done
```

### 2.2 Template Content Verification

#### Welcome Email
**Trigger**: User registration

**Content Checklist**:
- [ ] Subject: "Welcome to SkinGuard"
- [ ] Personalized greeting with user's name
- [ ] Brief introduction to platform
- [ ] Link to complete profile
- [ ] Link to upload first image
- [ ] Contact information
- [ ] Unsubscribe link
- [ ] Footer with company info

**Test**:
```bash
curl -X POST https://api.skinguard.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test+welcome@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "role": "patient"
  }'
```

#### Analysis Complete Email
**Trigger**: AI analysis completes

**Content Checklist**:
- [ ] Subject: "Your Skin Analysis Results Are Ready"
- [ ] Summary of AI findings
- [ ] Risk level indicator
- [ ] Link to view full report
- [ ] Medical disclaimer
- [ ] "Find a Doctor" CTA
- [ ] Unsubscribe link

**Test**:
```bash
# Upload image via API
curl -X POST https://api.skinguard.com/api/analyze-skin \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@test_lesion.jpg" \
  -F "symptoms={\"location\":\"arm\",\"sensations\":[\"itching\"],\"visual_changes\":[\"color\"]}"
```

#### Appointment Confirmation Email
**Trigger**: Appointment booked

**Content Checklist**:
- [ ] Subject: "Appointment Confirmed with Dr. [Name]"
- [ ] Appointment date and time
- [ ] Doctor name and clinic
- [ ] Consultation type (in-person/video)
- [ ] Video link (if video consultation)
- [ ] Calendar invite attachment
- [ ] Cancellation/rescheduling link
- [ ] Unsubscribe link

**Test**:
```bash
curl -X POST https://api.skinguard.com/api/appointments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": "DOCTOR_UUID",
    "scheduled_at": "2024-12-20T10:00:00Z",
    "consultation_type": "video"
  }'
```

#### 24-Hour Reminder Email
**Trigger**: 24 hours before appointment

**Content Checklist**:
- [ ] Subject: "Reminder: Appointment Tomorrow with Dr. [Name]"
- [ ] Appointment details
- [ ] Video link (if applicable)
- [ ] Preparation instructions
- [ ] Contact information
- [ ] Unsubscribe link

**Test**:
```bash
# Create appointment 24 hours in future
curl -X POST https://api.skinguard.com/api/appointments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"doctor_id\": \"DOCTOR_UUID\",
    \"scheduled_at\": \"$(date -u -d '+24 hours' +%Y-%m-%dT%H:%M:%SZ)\",
    \"consultation_type\": \"video\"
  }"

# Manually trigger reminder (for testing)
curl -X POST https://api.skinguard.com/api/admin/trigger-reminder/APPOINTMENT_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### Doctor Verification Email
**Trigger**: Admin approves doctor

**Content Checklist**:
- [ ] Subject: "Your SkinGuard Doctor Account Has Been Verified"
- [ ] Congratulations message
- [ ] Platform guidelines
- [ ] Link to doctor dashboard
- [ ] Getting started guide
- [ ] Support contact
- [ ] Unsubscribe link

**Test**:
```bash
curl -X PUT https://api.skinguard.com/api/admin/doctors/DOCTOR_ID/verify \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"verified": true}'
```

#### 6-Month Follow-Up Reminder
**Trigger**: 6 months after last screening

**Content Checklist**:
- [ ] Subject: "Time for Your Follow-Up Skin Screening"
- [ ] Reminder about last screening date
- [ ] Importance of regular screening
- [ ] Link to upload new image
- [ ] Educational content
- [ ] Unsubscribe link

**Test**:
```bash
# Manually trigger for test user
curl -X POST https://api.skinguard.com/api/admin/trigger-follow-up/USER_ID \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### Urgent Case Alert Email
**Trigger**: High-risk lesion detected (>85% probability)

**Content Checklist**:
- [ ] Subject: "URGENT: High-Risk Lesion Detected - Immediate Attention Required"
- [ ] Urgent warning message
- [ ] AI findings summary
- [ ] List of 3 nearest doctors
- [ ] Emergency consultation link
- [ ] Medical disclaimer
- [ ] Contact information

**Test**:
```bash
# Upload image that triggers high-risk detection
# (Use test image with known high-risk classification)
curl -X POST https://api.skinguard.com/api/analyze-skin \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@high_risk_test.jpg" \
  -F "symptoms={\"location\":\"face\",\"sensations\":[\"pain\"],\"visual_changes\":[\"size\",\"color\"]}"
```

---

## 3. Email Deliverability Testing

### 3.1 Spam Filter Testing

#### Test with Mail-Tester
```bash
# Get test email address
# Visit: https://www.mail-tester.com/
# Copy the test email address

# Send test email
curl -X POST https://api.skinguard.com/api/test/email/welcome \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient": "test-xxxxx@mail-tester.com"}'

# Check score on mail-tester.com
# Target: 8/10 or higher
```

**Common Issues and Fixes**:

| Issue | Score Impact | Fix |
|-------|--------------|-----|
| Missing SPF record | -2 points | Add SPF record to DNS |
| Missing DKIM | -2 points | Configure DKIM |
| No DMARC policy | -1 point | Add DMARC record |
| Broken links | -1 point | Fix all links |
| Missing unsubscribe | -1 point | Add unsubscribe link |
| Spammy content | -3 points | Revise email copy |

#### Test with GlockApps
```bash
# Visit: https://glockapps.com/
# Send test email to provided addresses
# Review deliverability report

# Target metrics:
# - Inbox placement: >95%
# - Spam folder: <5%
# - Missing: <1%
```

### 3.2 Inbox Placement Testing

#### Test Major Email Providers
**Providers to test**:
- [ ] Gmail
- [ ] Outlook/Hotmail
- [ ] Yahoo Mail
- [ ] Apple Mail (iCloud)
- [ ] ProtonMail

**Test Procedure**:
1. Create test accounts on each provider
2. Send test emails to each account
3. Check inbox placement (inbox vs spam)
4. Check email rendering
5. Test all links

**Test Script**:
```bash
# Test email addresses
TEST_EMAILS=(
  "test@gmail.com"
  "test@outlook.com"
  "test@yahoo.com"
  "test@icloud.com"
  "test@protonmail.com"
)

# Send test email to each
for email in "${TEST_EMAILS[@]}"; do
  echo "Sending to $email"
  curl -X POST https://api.skinguard.com/api/test/email/welcome \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"recipient\": \"$email\"}"
  sleep 2
done
```

**Verification Checklist** (for each provider):
- [ ] Email delivered to inbox (not spam)
- [ ] Email renders correctly
- [ ] Images load
- [ ] Links work
- [ ] Unsubscribe link works
- [ ] No security warnings

### 3.3 Email Rendering Testing

#### Test Email Clients
**Clients to test**:
- [ ] Gmail (web)
- [ ] Gmail (mobile app)
- [ ] Outlook (web)
- [ ] Outlook (desktop)
- [ ] Apple Mail (macOS)
- [ ] Apple Mail (iOS)
- [ ] Thunderbird

**Use Litmus or Email on Acid**:
```bash
# Visit: https://www.litmus.com/ or https://www.emailonacid.com/
# Send test email to provided address
# Review rendering across all clients
```

**Rendering Checklist**:
- [ ] Layout not broken
- [ ] Images display correctly
- [ ] Fonts render properly
- [ ] Colors correct
- [ ] Buttons clickable
- [ ] Links work
- [ ] Responsive on mobile
- [ ] No horizontal scrolling

---

## 4. Email Performance Testing

### 4.1 Delivery Speed Testing

#### Test Email Latency
```bash
# Send test email and measure time to delivery
START_TIME=$(date +%s)

curl -X POST https://api.skinguard.com/api/test/email/welcome \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient": "test@example.com"}'

# Check email arrival time
# Calculate: DELIVERY_TIME - START_TIME
```

**Target Latency**:
- [ ] Welcome email: < 30 seconds
- [ ] Analysis complete: < 1 minute
- [ ] Appointment confirmation: < 30 seconds
- [ ] Urgent alerts: < 15 seconds

### 4.2 Bulk Email Testing

#### Test High Volume Sending
```bash
# Send 100 emails
for i in {1..100}; do
  curl -X POST https://api.skinguard.com/api/test/email/welcome \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"recipient\": \"test+$i@example.com\"}" &
done

wait

# Check SendGrid/SES dashboard for:
# - Delivery rate
# - Bounce rate
# - Processing time
```

**Target Metrics**:
- [ ] Delivery rate: >98%
- [ ] Bounce rate: <2%
- [ ] Average processing time: <5 seconds
- [ ] No rate limit errors

### 4.3 Email Queue Testing

#### Test Queue Processing
```bash
# Create 50 appointments (triggers 50 emails)
for i in {1..50}; do
  curl -X POST https://api.skinguard.com/api/appointments \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"doctor_id\": \"DOCTOR_UUID\",
      \"scheduled_at\": \"$(date -u -d '+1 day' +%Y-%m-%dT%H:%M:%SZ)\",
      \"consultation_type\": \"video\"
    }" &
done

wait

# Monitor email queue
curl https://api.skinguard.com/api/admin/email-queue \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Verification**:
- [ ] All emails queued
- [ ] Queue processes without errors
- [ ] All emails delivered
- [ ] No emails stuck in queue

---

## 5. Email Bounce and Complaint Handling

### 5.1 Bounce Testing

#### Test Hard Bounces
```bash
# Send to invalid email
curl -X POST https://api.skinguard.com/api/test/email/welcome \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient": "invalid@nonexistentdomain12345.com"}'

# Check bounce notification
curl https://api.skinguard.com/api/admin/email-bounces \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Verification**:
- [ ] Bounce detected
- [ ] Bounce logged in database
- [ ] User email marked as invalid
- [ ] No further emails sent to bounced address

#### Test Soft Bounces
```bash
# Send to full mailbox (simulate)
# Check retry logic
```

**Verification**:
- [ ] Soft bounce detected
- [ ] Email retried (up to 3 times)
- [ ] Marked as hard bounce after retries exhausted

### 5.2 Complaint Handling

#### Test Spam Complaints
```bash
# Mark test email as spam in Gmail/Outlook
# Check complaint notification

curl https://api.skinguard.com/api/admin/email-complaints \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Verification**:
- [ ] Complaint detected
- [ ] Complaint logged
- [ ] User automatically unsubscribed
- [ ] Admin notified (if complaint rate high)

### 5.3 Unsubscribe Testing

#### Test Unsubscribe Link
```bash
# Send test email
curl -X POST https://api.skinguard.com/api/test/email/welcome \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient": "test@example.com"}'

# Click unsubscribe link in email
# Verify unsubscribe page loads

# Check unsubscribe status
curl https://api.skinguard.com/api/users/test@example.com/email-preferences \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Verification**:
- [ ] Unsubscribe link present in all emails
- [ ] Unsubscribe page loads
- [ ] User can select email preferences
- [ ] Unsubscribe processed immediately
- [ ] Confirmation message shown
- [ ] No further marketing emails sent
- [ ] Transactional emails still sent (appointments, etc.)

---

## 6. Email Security Testing

### 6.1 SPF Verification

```bash
# Check SPF record
dig TXT skinguard.com | grep "v=spf1"

# Test SPF with email
# Send email and check headers
curl -X POST https://api.skinguard.com/api/test/email/welcome \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient": "test@example.com"}'

# Check email headers for SPF result
# Look for: Received-SPF: pass
```

**Expected SPF Record**:
```
v=spf1 include:sendgrid.net ~all
```

**SPF Result**:
- [ ] SPF: pass

### 6.2 DKIM Verification

```bash
# Check DKIM record
dig TXT s1._domainkey.skinguard.com

# Check email headers for DKIM signature
# Look for: DKIM-Signature: v=1; a=rsa-sha256; ...
# Look for: Authentication-Results: dkim=pass
```

**DKIM Result**:
- [ ] DKIM: pass

### 6.3 DMARC Verification

```bash
# Check DMARC record
dig TXT _dmarc.skinguard.com

# Check email headers for DMARC result
# Look for: Authentication-Results: dmarc=pass
```

**Expected DMARC Record**:
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@skinguard.com; pct=100
```

**DMARC Result**:
- [ ] DMARC: pass

### 6.4 Email Header Analysis

```bash
# Get full email headers
# Forward test email to: check-auth@verifier.port25.com
# Review authentication results
```

**Expected Results**:
- [ ] SPF: pass
- [ ] DKIM: pass
- [ ] DMARC: pass
- [ ] No authentication failures

---

## 7. Monitoring and Alerts

### 7.1 Email Metrics Dashboard

**Metrics to Monitor**:
- [ ] Emails sent (daily)
- [ ] Delivery rate (%)
- [ ] Bounce rate (%)
- [ ] Complaint rate (%)
- [ ] Open rate (%)
- [ ] Click rate (%)
- [ ] Unsubscribe rate (%)

**Access Metrics**:

**SendGrid**:
```bash
# Get email statistics
curl -X GET "https://api.sendgrid.com/v3/stats?start_date=$(date -d '7 days ago' +%Y-%m-%d)" \
  -H "Authorization: Bearer $SENDGRID_API_KEY"
```

**AWS SES**:
```bash
# Get send statistics
aws ses get-send-statistics

# Get bounce and complaint metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/SES \
  --metric-name Bounce \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum
```

### 7.2 Alert Configuration

#### High Bounce Rate Alert
```bash
# Alert if bounce rate > 5%
# Configure in SendGrid/SES dashboard or monitoring tool
```

#### High Complaint Rate Alert
```bash
# Alert if complaint rate > 0.1%
# Configure in SendGrid/SES dashboard or monitoring tool
```

#### Delivery Failure Alert
```bash
# Alert if delivery rate < 95%
# Configure in SendGrid/SES dashboard or monitoring tool
```

### 7.3 Email Logs

```bash
# View recent email logs
curl https://api.skinguard.com/api/admin/email-logs?limit=100 \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Search email logs
curl "https://api.skinguard.com/api/admin/email-logs?recipient=test@example.com&status=bounced" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 8. Production Testing Checklist

### 8.1 Pre-Launch Testing
- [ ] All email templates tested
- [ ] Spam score > 8/10
- [ ] Inbox placement > 95%
- [ ] Email rendering correct in all major clients
- [ ] All links work
- [ ] Unsubscribe link present and functional
- [ ] SPF, DKIM, DMARC configured and passing
- [ ] Bounce handling configured
- [ ] Complaint handling configured
- [ ] Email queue processing correctly
- [ ] Monitoring and alerts configured

### 8.2 Post-Launch Monitoring (First Week)
- [ ] Monitor delivery rate daily
- [ ] Monitor bounce rate daily
- [ ] Monitor complaint rate daily
- [ ] Review email logs for errors
- [ ] Check user feedback on emails
- [ ] Verify all automated emails sending
- [ ] Check email latency

### 8.3 Ongoing Maintenance
- [ ] Review email metrics weekly
- [ ] Update email templates as needed
- [ ] Monitor spam score monthly
- [ ] Review and update email content
- [ ] Test new email clients/providers
- [ ] Keep SPF/DKIM/DMARC records updated
- [ ] Review and optimize email performance

---

## 9. Troubleshooting

### 9.1 Emails Not Delivering

**Check**:
1. API key valid
2. Domain verified
3. Sender email verified
4. Not in sandbox mode (AWS SES)
5. Sending limits not exceeded
6. Recipient email valid
7. No bounces/complaints for recipient

**Debug**:
```bash
# Check SendGrid activity
curl -X GET "https://api.sendgrid.com/v3/messages?limit=10" \
  -H "Authorization: Bearer $SENDGRID_API_KEY"

# Check AWS SES send quota
aws ses get-send-quota
```

### 9.2 Emails Going to Spam

**Check**:
1. SPF record configured
2. DKIM configured
3. DMARC policy set
4. Email content not spammy
5. Unsubscribe link present
6. Sender reputation good

**Fix**:
- Warm up IP address (gradually increase volume)
- Improve email content
- Remove spam trigger words
- Add plain text version
- Authenticate domain properly

### 9.3 High Bounce Rate

**Check**:
1. Email list quality
2. Email validation on signup
3. Bounce handling configured
4. Remove bounced emails from list

**Fix**:
```bash
# Get bounced emails
curl https://api.skinguard.com/api/admin/email-bounces \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Mark emails as invalid
curl -X POST https://api.skinguard.com/api/admin/mark-invalid-emails \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"emails": ["bounced1@example.com", "bounced2@example.com"]}'
```

---

**Tested By**: _________________  
**Date**: _________________  
**Delivery Rate**: _________________  
**Spam Score**: _________________  
**Issues Found**: _________________
