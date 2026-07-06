# Urgent Case Escalation System

## Overview

The Urgent Case Escalation System is a background job scheduler that monitors unreviewed urgent skin cancer cases and automatically escalates them to system administrators after 24 hours.

**Requirements**: 23.6

## Architecture

### Components

1. **UrgentCaseEscalationService** (`app/scheduler.py`)
   - Core service for checking and escalating unreviewed urgent cases
   - Sends email notifications to administrators
   - Tracks escalations in audit logs to prevent duplicates

2. **Background Scheduler** (`app/scheduler.py`)
   - Uses APScheduler to run escalation checks every hour
   - Automatically starts on application startup
   - Gracefully shuts down on application shutdown

3. **Email Notifications** (`app/email_service.py`)
   - Sends detailed escalation emails to all admin users
   - Includes case details, time elapsed, and recommended actions

## How It Works

### 1. Escalation Trigger

An urgent case is escalated when ALL of the following conditions are met:

- Report status is `"urgent"` (AI detected cancer probability > 85%)
- Report was created more than 24 hours ago
- Report has no consultation notes (unreviewed)
- Report has not been previously escalated

### 2. Escalation Process

Every hour, the background scheduler:

1. **Queries Database**: Finds all urgent cases meeting escalation criteria
2. **Gets Admin List**: Retrieves all users with role `"admin"`
3. **Checks Escalation Status**: Verifies case hasn't been escalated before
4. **Sends Notifications**: Emails all admins with case details
5. **Tracks Escalation**: Creates audit log entry to prevent duplicates

### 3. Email Content

Admin escalation emails include:

- **Case Details**:
  - Report ID
  - Patient name and email
  - Risk level (URGENT)
  - AI prediction (cancer type and probability)
  - Time elapsed since submission

- **Context**:
  - Why escalation occurred (24+ hours unreviewed)
  - Which doctors were originally notified

- **Recommended Actions**:
  - Review case in admin panel
  - Contact patient directly
  - Follow up with notified doctors
  - Consider emergency services if needed

- **Direct Link**: Button to view case in admin panel

## Configuration

### Environment Variables

The escalation system uses the same email configuration as the emergency referral system:

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@skinguard.com
FROM_NAME=SkinGuard AI
```

### Scheduler Settings

The escalation check runs every hour by default. To modify:

```python
# In app/scheduler.py, modify the IntervalTrigger
_scheduler.add_job(
    check_urgent_cases_job,
    trigger=IntervalTrigger(hours=1),  # Change this value
    id="check_urgent_cases",
    name="Check Unreviewed Urgent Cases",
    replace_existing=True
)
```

### Escalation Threshold

The 24-hour threshold can be modified:

```python
# In app/scheduler.py, UrgentCaseEscalationService.__init__
self.escalation_threshold_hours = 24  # Change this value
```

## Database Schema

### Audit Log Entry

Escalations are tracked in the `audit_logs` table:

```sql
{
  "user_id": null,  -- System action
  "action": "urgent_case_escalation",
  "resource_type": "medical_report",
  "resource_id": "report-uuid",
  "metadata": {
    "escalation_timestamp": "2024-02-10T12:00:00Z",
    "reason": "Unreviewed urgent case for 24+ hours"
  },
  "ip_address": null
}
```

## API Integration

### Application Lifecycle

The scheduler is integrated into the FastAPI application lifecycle:

```python
# In app/main.py

@app.on_event("startup")
async def startup_event():
    """Start background scheduler on application startup"""
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on application shutdown"""
    stop_scheduler()
```

### Manual Trigger (Development/Testing)

For testing or manual escalation checks:

```python
from app.scheduler import get_escalation_service

# Get service instance
escalation_service = get_escalation_service()

# Run escalation check manually
stats = await escalation_service.process_escalations()

print(f"Cases checked: {stats['cases_checked']}")
print(f"Cases escalated: {stats['cases_escalated']}")
print(f"Notifications sent: {stats['notifications_sent']}")
```

## Monitoring

### Logs

The escalation system logs all activities:

```python
# Successful escalation
INFO: Escalated report report-123: 2/2 notifications sent

# No cases requiring escalation
INFO: No cases requiring escalation

# Already escalated case
INFO: Report report-123 already escalated, skipping

# Error handling
ERROR: Error in process_escalations: [error details]
```

### Statistics

Each escalation run returns statistics:

```python
{
    "cases_checked": 3,      # Number of unreviewed urgent cases found
    "cases_escalated": 2,    # Number of cases escalated (excluding duplicates)
    "notifications_sent": 4  # Total emails sent (2 cases × 2 admins)
}
```

## Testing

### Unit Tests

Located in `tests/unit/test_urgent_escalation.py`:

- Test case detection logic
- Test admin email retrieval
- Test notification content
- Test escalation tracking
- Test duplicate prevention
- Test error handling

Run with:
```bash
pytest tests/unit/test_urgent_escalation.py -v
```

### Property-Based Tests

Located in `tests/property/test_urgent_escalation_properties.py`:

- Property 84: Urgent Case Escalation
- Tests escalation across various case scenarios
- Verifies 24-hour threshold
- Validates email content completeness
- Tests duplicate prevention

Run with:
```bash
pytest tests/property/test_urgent_escalation_properties.py -v
```

## Error Handling

### No Admin Users

If no admin users exist:
- Logs warning: "No admin users found - cannot send escalation notifications"
- Returns statistics with 0 escalations
- Does not crash or throw exceptions

### Email Failures

If email sending fails:
- Logs error for specific admin
- Continues attempting to notify other admins
- Only tracks escalation if at least one notification succeeds

### Database Errors

If database queries fail:
- Logs error with full traceback
- Returns empty results
- Scheduler continues running for next iteration

## Production Considerations

### Performance

- Escalation checks run every hour (low frequency)
- Queries are indexed on `status`, `created_at`, and `consultation_notes`
- Minimal database load (only queries urgent cases)

### Scalability

- Service is stateless (can run on multiple instances)
- Uses database for coordination (audit logs prevent duplicates)
- Email sending is async and non-blocking

### Reliability

- Scheduler automatically restarts on application restart
- Failed escalations are retried on next hourly check
- Audit logs ensure no duplicate notifications

### Monitoring Recommendations

1. **Alert on No Admins**: Monitor for "No admin users found" logs
2. **Alert on Email Failures**: Track email sending success rate
3. **Track Escalation Rate**: Monitor number of cases requiring escalation
4. **Response Time**: Track time from escalation to case review

## Future Enhancements

Potential improvements:

1. **Configurable Thresholds**: Allow per-case or per-risk-level thresholds
2. **Escalation Levels**: Multi-tier escalation (24h → admins, 48h → emergency)
3. **SMS Notifications**: Add SMS alerts for critical escalations
4. **Dashboard Integration**: Real-time escalation status in admin panel
5. **Auto-Assignment**: Automatically assign escalated cases to available admins
6. **Escalation History**: Track full escalation timeline per case

## Related Systems

- **Emergency Referral System** (`app/emergency_referral.py`): Initial notification to nearest doctors
- **Email Service** (`app/email_service.py`): Shared email infrastructure
- **Audit System** (`app/audit.py`): Tracks all escalation events

## Support

For issues or questions:
- Check logs for error messages
- Verify email configuration
- Ensure admin users exist in database
- Test email service independently
- Review audit logs for escalation history
