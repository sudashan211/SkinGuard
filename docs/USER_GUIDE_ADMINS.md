# SkinGuard Admin User Guide

Welcome to the SkinGuard Admin Panel! This guide will help you manage the platform, verify doctors, moderate content, and monitor system health.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Admin Dashboard Overview](#admin-dashboard-overview)
3. [Doctor Verification](#doctor-verification)
4. [Content Moderation](#content-moderation)
5. [Analytics and Monitoring](#analytics-and-monitoring)
6. [Skin-Wiki Management](#skin-wiki-management)
7. [User Management](#user-management)
8. [System Health Monitoring](#system-health-monitoring)
9. [Security and Audit Logs](#security-and-audit-logs)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Getting Started

### Admin Access

Admin accounts are created by system administrators. If you need admin access:
1. Contact the technical team
2. Provide your email address
3. Your account will be created with admin role
4. You'll receive login credentials via secure channel

### First Login

1. Visit https://skinguard.com/admin
2. Log in with your admin credentials
3. Complete two-factor authentication setup
4. Review the admin dashboard

### Admin Responsibilities

As an admin, you are responsible for:
- **Doctor Verification:** Reviewing and approving doctor applications
- **Content Moderation:** Reviewing flagged content and NSFW violations
- **Platform Monitoring:** Tracking usage, performance, and errors
- **Content Management:** Updating educational content in Skin-Wiki
- **User Support:** Handling escalated user issues
- **Security:** Monitoring audit logs and security events

## Admin Dashboard Overview

### Dashboard Layout

The admin dashboard provides a comprehensive view of platform health:

**Top Metrics (Real-time):**
- Daily Active Users
- Total Screenings Today
- Pending Doctor Verifications
- Flagged Content Items
- Average Processing Time
- Error Rate

**Quick Actions:**
- Verify Doctors
- Review Flagged Content
- View Analytics
- Manage Skin-Wiki
- View Audit Logs

**Recent Activity:**
- Latest doctor applications
- Recent flagged content
- System alerts
- User reports

### Navigation

**Main Menu:**
- **Dashboard:** Overview and metrics
- **Doctors:** Verification and management
- **Content:** Moderation and flagging
- **Analytics:** Usage and performance data
- **Skin-Wiki:** Educational content management
- **Users:** User management and support
- **System:** Health monitoring and logs
- **Settings:** Platform configuration

## Doctor Verification

### Verification Workflow

#### Step 1: View Pending Applications

1. Go to **Doctors** > **Pending Verifications**
2. See list of doctors awaiting verification
3. Each entry shows:
   - Doctor name and email
   - License number
   - Clinic name and location
   - Specialization
   - Application date
   - Status: Pending

#### Step 2: Review Application

Click on a doctor to see full details:

**Personal Information:**
- Full name
- Email address
- Phone number
- Professional photo

**Credentials:**
- Medical license number
- State/country of licensure
- License expiration date
- Board certifications

**Practice Information:**
- Clinic name
- Full address
- Coordinates (lat/lng)
- WhatsApp number
- Specialization
- Years of experience
- Languages spoken

**Supporting Documents:**
- License verification documents
- Clinic registration
- Professional references

#### Step 3: Verify Credentials

**License Verification:**
1. Copy the license number
2. Visit state medical board website
3. Search for the license
4. Verify:
   - License is active
   - Name matches
   - No disciplinary actions
   - Specialization is correct

**Common Medical Board Websites:**
- **US:** https://www.fsmb.org/fcvs/
- **UK:** https://www.gmc-uk.org/
- **Canada:** https://www.cpsbc.ca/
- **Australia:** https://www.ahpra.gov.au/

**Clinic Verification:**
1. Search clinic name online
2. Verify address matches
3. Check Google Maps for clinic location
4. Look for online reviews and presence

**Red Flags:**
- License not found or expired
- Name mismatch
- Disciplinary actions on record
- Clinic address doesn't exist
- Suspicious or incomplete information
- No online presence

#### Step 4: Make Decision

**To Approve:**
1. Click "Approve" button
2. Add verification notes (optional)
3. Confirm approval
4. Doctor receives email notification
5. Profile becomes visible to patients

**To Reject:**
1. Click "Reject" button
2. Select rejection reason:
   - Invalid license
   - Expired credentials
   - Incomplete information
   - Failed verification
   - Other (specify)
3. Add detailed notes
4. Confirm rejection
5. Doctor receives email with reason

**To Request More Information:**
1. Click "Request Info" button
2. Specify what's needed
3. Doctor receives email
4. Application status: "Info Requested"
5. Review again when doctor responds

### Verification Best Practices

**Do:**
- Verify every license with official sources
- Check for disciplinary actions
- Verify clinic exists and is legitimate
- Document your verification process
- Respond within 1-3 business days
- Be thorough but fair

**Don't:**
- Approve without proper verification
- Reject without clear reason
- Share doctor information publicly
- Make assumptions without verification
- Rush the verification process

### Managing Verified Doctors

**View All Doctors:**
1. Go to **Doctors** > **All Doctors**
2. Filter by:
   - Verification status
   - Specialization
   - Location
   - Rating
   - Activity level

**Doctor Actions:**
- **View Profile:** See complete doctor information
- **Suspend:** Temporarily disable doctor account
- **Revoke Verification:** Remove verified status
- **View Activity:** See consultations and reviews
- **Contact:** Send message to doctor

**Suspension Reasons:**
- Multiple patient complaints
- Low ratings (< 3.0)
- Inactive for extended period
- Policy violations
- Under investigation

**To Suspend a Doctor:**
1. Go to doctor's profile
2. Click "Suspend Account"
3. Select reason
4. Set suspension duration or indefinite
5. Add notes
6. Confirm suspension
7. Doctor receives notification

**To Reactivate:**
1. Go to suspended doctor's profile
2. Review suspension reason
3. Click "Reactivate"
4. Add notes about resolution
5. Confirm reactivation

## Content Moderation

### Flagged Content Overview

Content is automatically flagged when:
- NSFW score > 0.35
- Non-skin score > 0.8
- User reports inappropriate content
- AI detects policy violations

### Reviewing Flagged Content

#### Step 1: Access Flagged Content

1. Go to **Content** > **Flagged Reports**
2. See list of flagged items
3. Sort by:
   - Date flagged
   - NSFW score
   - Severity
   - Status (pending, reviewed, removed)

#### Step 2: Review Content

Click on a flagged item to see:

**Image Information:**
- Thumbnail and full-resolution image
- Upload date and time
- Patient ID (anonymized)
- NSFW score
- Non-skin score
- Rejection reason

**AI Analysis:**
- Detection confidence
- Content categories detected
- Risk assessment

**User Context:**
- Patient's upload history
- Previous violations
- Account age

**Audit Trail:**
- When flagged
- Automatic actions taken
- Previous admin reviews

#### Step 3: Make Decision

**Content is Legitimate Medical Image:**
1. Click "Approve"
2. Add notes: "Legitimate medical image, false positive"
3. Image is unflagged
4. Patient can view results
5. AI threshold may be adjusted

**Content is Inappropriate:**
1. Click "Confirm Removal"
2. Select violation type:
   - NSFW content
   - Non-medical image
   - Spam
   - Other
3. Add notes
4. Decide on user action:
   - Warning
   - Temporary suspension
   - Permanent ban
5. Confirm removal
6. Patient receives notification

**Unclear/Borderline:**
1. Click "Request Second Review"
2. Add notes about concerns
3. Another admin reviews
4. Decision made by consensus

### Content Moderation Guidelines

**NSFW Content:**
- Explicit sexual content
- Nudity not related to medical screening
- Inappropriate body parts
- Suggestive poses

**Non-Medical Content:**
- Random objects
- Memes or jokes
- Screenshots
- Text images
- Non-skin images

**Legitimate Medical Images:**
- Skin lesions on any body part
- Moles, birthmarks, rashes
- Post-surgical scars
- Dermatological conditions
- May include partial nudity if medically necessary

**When in Doubt:**
- Err on the side of caution
- Request second opinion
- Consider context and patient history
- Document reasoning

### User Actions

**Warning:**
- First-time minor violation
- Likely accidental
- Send warning email
- No account restrictions

**Temporary Suspension:**
- Repeated violations
- Moderate severity
- Suspend for 7-30 days
- User can appeal

**Permanent Ban:**
- Severe violations
- Repeated offenses after warnings
- Malicious intent
- No appeal

**To Ban a User:**
1. Go to **Users** > **Search**
2. Find user by ID or email
3. Click "Ban User"
4. Select reason
5. Add detailed notes
6. Confirm ban
7. User receives notification

## Analytics and Monitoring

### Platform Analytics

#### Usage Metrics

**Dashboard View:**
1. Go to **Analytics** > **Overview**
2. Select date range
3. View metrics:
   - Daily Active Users (DAU)
   - Monthly Active Users (MAU)
   - Total Screenings
   - New User Registrations
   - Doctor Consultations
   - Appointment Bookings

**Detailed Reports:**
- User growth trends
- Screening volume by day/week/month
- Peak usage times
- User retention rates
- Conversion rates (screening → consultation)

#### Performance Metrics

**System Performance:**
- Average API response time
- AI processing time (Gatekeeper, Medical AI)
- Database query performance
- Storage usage
- Bandwidth usage

**Error Tracking:**
- Error rate (%)
- Error types and frequency
- Failed uploads
- API failures
- Timeout incidents

**Quality Metrics:**
- Image quality rejection rate
- NSFW detection accuracy
- AI prediction confidence
- User satisfaction scores

#### Medical Analytics

**Cancer Type Distribution:**
- Melanoma detections
- Basal Cell Carcinoma
- Squamous Cell Carcinoma
- Other types
- Trends over time

**Risk Level Distribution:**
- Low risk cases
- Medium risk cases
- High risk cases
- Urgent cases
- Emergency referrals

**Geographic Distribution:**
- Users by country/region
- Doctors by location
- Screening density maps
- Underserved areas

#### Doctor Analytics

**Doctor Performance:**
- Consultations completed
- Average rating
- Response time
- Patient satisfaction
- Specialization distribution

**Appointment Metrics:**
- Total appointments
- Completion rate
- Cancellation rate
- Video vs in-person ratio
- Average wait time

### Exporting Reports

**To Export Data:**
1. Go to desired analytics page
2. Select date range and filters
3. Click "Export"
4. Choose format:
   - CSV (for spreadsheets)
   - JSON (for data analysis)
   - PDF (for reports)
5. Download file

**Scheduled Reports:**
1. Go to **Analytics** > **Scheduled Reports**
2. Click "Create Report"
3. Configure:
   - Report type
   - Frequency (daily, weekly, monthly)
   - Recipients
   - Format
4. Save schedule
5. Reports sent automatically

## Skin-Wiki Management

### Content Structure

Skin-Wiki contains educational articles about:
- 7 types of skin cancer
- Risk factors and prevention
- Self-examination guides
- Treatment options
- FAQs

### Managing Articles

#### Creating New Article

1. Go to **Skin-Wiki** > **Articles**
2. Click "Create Article"
3. Fill in details:
   - Title
   - Category (cancer type, prevention, etc.)
   - Content (rich text editor)
   - Images
   - References
   - Author
4. Add translations for all supported languages
5. Preview article
6. Click "Publish"

#### Editing Existing Article

1. Go to **Skin-Wiki** > **Articles**
2. Find article to edit
3. Click "Edit"
4. Make changes
5. Version is automatically saved
6. Add change notes
7. Click "Update"

**Version History:**
- All changes are tracked
- Can view previous versions
- Can revert to previous version
- Shows who made changes and when

#### Article Guidelines

**Content Quality:**
- Medically accurate
- Cite reputable sources
- Use clear, simple language
- Include visual aids
- Keep updated with latest research

**Required Sections:**
- Overview
- Symptoms
- Risk factors
- Diagnosis
- Treatment options
- Prevention
- When to see a doctor
- References

**Images:**
- High quality
- Properly labeled
- Include captions
- Respect copyright
- Medical accuracy

### Translation Management

**Adding Translations:**
1. Open article
2. Click "Translations"
3. Select language
4. Translate all fields
5. Have native speaker review
6. Publish translation

**Supported Languages:**
- English (EN)
- Spanish (ES)
- French (FR)
- German (DE)
- Mandarin Chinese (ZH)

**Translation Quality:**
- Use professional translators
- Medical terminology must be accurate
- Cultural sensitivity
- Regular reviews and updates

### Content Review Process

**Quarterly Review:**
1. Review all articles for accuracy
2. Update with latest research
3. Check broken links
4. Update statistics
5. Refresh images if needed
6. Verify translations

**Medical Review:**
- Have dermatologist review content
- Verify medical accuracy
- Update treatment guidelines
- Ensure compliance with medical standards

## User Management

### User Search and Management

**Finding Users:**
1. Go to **Users** > **Search**
2. Search by:
   - Email
   - Name
   - User ID
   - Role
3. View user profile

**User Profile Information:**
- Account details
- Role and verification status
- Activity history
- Reports submitted
- Appointments booked
- Violations and warnings

**User Actions:**
- View full profile
- Reset password
- Change role
- Suspend account
- Ban user
- Delete account
- Send message

### Handling User Issues

**Common Issues:**

**1. Account Access Problems:**
- Reset password
- Verify email
- Unlock account
- Restore suspended account

**2. Data Issues:**
- Recover deleted reports
- Fix incorrect data
- Merge duplicate accounts
- Export user data

**3. Privacy Requests:**
- Data export (GDPR)
- Account deletion
- Data correction
- Opt-out requests

**4. Billing Issues:**
- Refund requests
- Subscription problems
- Payment failures

### Privacy and Data Protection

**GDPR Compliance:**
- Right to access data
- Right to deletion
- Right to correction
- Right to data portability
- Right to object

**Handling Data Requests:**
1. Verify user identity
2. Process request within 30 days
3. Export data in machine-readable format
4. Confirm completion with user
5. Document in audit log

**Account Deletion:**
1. User requests deletion
2. Verify identity
3. 30-day grace period
4. Anonymize medical data (keep for research)
5. Delete personal information
6. Confirm deletion
7. Cannot be reversed after 30 days

## System Health Monitoring

### Health Dashboard

**Real-time Monitoring:**
1. Go to **System** > **Health**
2. View system status:
   - API Status: Healthy/Degraded/Down
   - Database: Connected/Slow/Down
   - AI Models: Loaded/Loading/Error
   - Storage: Available/Full/Error
   - Email Service: Active/Failed
   - Video Service: Active/Failed

**Performance Metrics:**
- CPU usage
- Memory usage
- Disk space
- Network bandwidth
- Active connections
- Queue lengths

### Alerts and Notifications

**Alert Types:**
- **Critical:** System down, data loss risk
- **High:** Performance degradation, errors
- **Medium:** Warnings, capacity concerns
- **Low:** Informational, maintenance

**Alert Channels:**
- Email notifications
- SMS for critical alerts
- In-app notifications
- Slack/Teams integration

**Configuring Alerts:**
1. Go to **System** > **Alerts**
2. Click "Configure"
3. Set thresholds:
   - Response time > 5 seconds
   - Error rate > 5%
   - CPU usage > 80%
   - Disk space < 20%
4. Choose notification channels
5. Save configuration

### Incident Response

**When Alert Triggers:**
1. Assess severity
2. Check system health dashboard
3. Review error logs
4. Identify root cause
5. Take corrective action
6. Monitor resolution
7. Document incident
8. Post-mortem if critical

**Common Issues:**

**High Response Times:**
- Check database performance
- Review slow queries
- Check AI model loading
- Verify network connectivity

**High Error Rates:**
- Check error logs
- Identify error patterns
- Fix bugs or configuration
- Deploy hotfix if needed

**Storage Issues:**
- Check disk space
- Clean up old logs
- Archive old images
- Increase storage capacity

**Database Issues:**
- Check connection pool
- Review slow queries
- Optimize indexes
- Scale database if needed

## Security and Audit Logs

### Audit Log Review

**Accessing Audit Logs:**
1. Go to **System** > **Audit Logs**
2. Filter by:
   - Date range
   - User
   - Action type
   - Resource type
   - Severity

**Logged Events:**
- User authentication (login, logout)
- Account changes (role, permissions)
- Doctor verification actions
- Content moderation decisions
- Data access (viewing reports)
- Data modifications
- System configuration changes
- Security events

**Log Entry Details:**
- Timestamp
- User ID and email
- Action performed
- Resource affected
- IP address
- User agent
- Result (success/failure)
- Additional metadata

### Security Monitoring

**Security Events to Monitor:**
- Failed login attempts
- Unauthorized access attempts
- Privilege escalation attempts
- Data export requests
- Account deletions
- Configuration changes
- Suspicious activity patterns

**Investigating Security Incidents:**
1. Review audit logs
2. Identify affected users/data
3. Assess impact
4. Take immediate action (suspend accounts, revoke access)
5. Investigate root cause
6. Implement fixes
7. Document incident
8. Report if required (data breach)

### Compliance and Reporting

**Regulatory Compliance:**
- HIPAA (US healthcare data)
- GDPR (EU data protection)
- CCPA (California privacy)
- Local healthcare regulations

**Compliance Reports:**
1. Go to **System** > **Compliance**
2. Generate reports:
   - Data access logs
   - User consent records
   - Data retention compliance
   - Security incidents
   - Privacy requests handled
3. Export for auditors

**Regular Audits:**
- Quarterly security audits
- Annual compliance reviews
- Penetration testing
- Vulnerability assessments

## Best Practices

### Doctor Verification

- Verify every license with official sources
- Document verification process
- Respond within 1-3 business days
- Be consistent in standards
- Keep verification notes detailed

### Content Moderation

- Review flagged content daily
- Be fair and consistent
- Document decisions clearly
- Escalate unclear cases
- Respect user privacy

### System Monitoring

- Check health dashboard daily
- Review error logs weekly
- Monitor performance trends
- Set up proactive alerts
- Plan capacity ahead of time

### User Support

- Respond to issues promptly
- Be professional and empathetic
- Document all interactions
- Escalate complex issues
- Follow up on resolutions

### Security

- Review audit logs regularly
- Monitor for suspicious activity
- Keep systems updated
- Follow security protocols
- Report incidents immediately

## Troubleshooting

### Common Admin Issues

#### Can't Access Admin Panel

**Problem:** Login fails or access denied

**Solutions:**
1. Verify you have admin role
2. Check email and password
3. Clear browser cache
4. Try different browser
5. Contact technical team

#### Doctor Verification Not Working

**Problem:** Can't approve/reject doctors

**Solutions:**
1. Check internet connection
2. Verify you have permissions
3. Refresh the page
4. Check if doctor already processed
5. Review error message

#### Analytics Not Loading

**Problem:** Dashboard shows no data

**Solutions:**
1. Check date range selected
2. Verify data exists for period
3. Clear browser cache
4. Check database connection
5. Contact technical team

#### Can't Update Skin-Wiki

**Problem:** Changes not saving

**Solutions:**
1. Check internet connection
2. Verify you have edit permissions
3. Check for validation errors
4. Try saving again
5. Contact technical team

### Getting Help

**Technical Support:**
- Email: admin-support@skinguard.com
- Phone: +1-XXX-XXX-XXXX
- Response time: 1-4 hours

**Documentation:**
- Admin manual: https://docs.skinguard.com/admin
- API docs: https://docs.skinguard.com/api
- Video tutorials: https://learn.skinguard.com

**Emergency Contact:**
- Critical issues: emergency@skinguard.com
- Security incidents: security@skinguard.com
- 24/7 on-call: +1-XXX-XXX-XXXX

---

## Quick Reference

### Daily Tasks
- [ ] Review pending doctor verifications
- [ ] Check flagged content
- [ ] Monitor system health
- [ ] Review critical alerts
- [ ] Respond to user issues

### Weekly Tasks
- [ ] Review analytics reports
- [ ] Check error logs
- [ ] Update Skin-Wiki if needed
- [ ] Review security logs
- [ ] Team sync meeting

### Monthly Tasks
- [ ] Generate compliance reports
- [ ] Review doctor performance
- [ ] Analyze usage trends
- [ ] Update documentation
- [ ] Security audit

### Quarterly Tasks
- [ ] Comprehensive system review
- [ ] Update educational content
- [ ] Review and update policies
- [ ] Performance optimization
- [ ] Disaster recovery test

---

**Admin Guide Version**: 1.0  
**Last Updated**: February 2026  
**For Support**: admin-support@skinguard.com
