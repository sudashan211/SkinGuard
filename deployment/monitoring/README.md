# SkinGuard Monitoring and Logging

This directory contains monitoring, logging, and alerting configurations for the SkinGuard platform.

## Components

### 1. Error Tracking (Sentry)

**File:** `sentry.config.py`

Sentry provides real-time error tracking and performance monitoring.

**Features:**
- Automatic error capture with stack traces
- Performance monitoring for API endpoints
- Database query monitoring
- Custom context enrichment
- PII filtering for HIPAA compliance

**Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SENTRY_DSN="your-sentry-dsn"
export ENVIRONMENT="production"
export RELEASE_VERSION="1.0.0"

# Initialize in your application
from deployment.monitoring.sentry_config import init_sentry
init_sentry()
```

**Usage:**
```python
from deployment.monitoring.sentry_config import (
    capture_exception_with_context,
    capture_message_with_context,
    start_transaction
)

# Capture exception with context
try:
    process_image()
except Exception as e:
    capture_exception_with_context(
        e,
        user_id="user-123",
        report_id="report-456"
    )

# Performance monitoring
with start_transaction(name="ai-analysis", op="ai.process") as transaction:
    with transaction.start_child(op="ai.nsfw", description="NSFW check"):
        check_nsfw(image)
```

### 2. Structured Logging

**Files:** `logging.config.yaml`, `logger.py`

Provides structured logging with JSON format for log aggregation.

**Features:**
- Multiple log handlers (console, file, CloudWatch)
- Structured JSON logging
- Context enrichment
- Specialized loggers (API, AI, Security)
- Log rotation

**Setup:**
```bash
# Create log directory
sudo mkdir -p /var/log/skinguard
sudo chown $USER:$USER /var/log/skinguard

# Configure AWS credentials for CloudWatch (production)
aws configure
```

**Usage:**
```python
from deployment.monitoring.logger import get_logger, log_execution

# Get specialized logger
api_logger = get_logger("app.api", logger_type="api")
ai_logger = get_logger("app.ai", logger_type="ai")
security_logger = get_logger("app.security", logger_type="security")

# Log API request
api_logger.log_request("POST", "/api/analyze-skin", user_id="user-123")

# Log AI analysis
ai_logger.log_analysis_start("report-123", (512, 512))
ai_logger.log_analysis_complete("report-123", 2500, predictions)

# Log security event
security_logger.log_auth_failure("user@example.com", "invalid_password")

# Use decorator for automatic logging
@log_execution(api_logger)
def process_request():
    pass
```

### 3. Alerting System

**Files:** `alerts.config.yaml`, `alerting.py`

Configurable alerting system with multiple channels.

**Features:**
- Multiple alert channels (Email, Slack, PagerDuty, SMS)
- Configurable alert rules
- Cooldown periods to prevent alert spam
- Alert templates
- Escalation policies
- Maintenance windows

**Alert Channels:**
- **Email:** SMTP-based email alerts
- **Slack:** Webhook-based Slack notifications
- **PagerDuty:** Incident management integration
- **SMS:** Twilio-based SMS alerts

**Setup:**
```bash
# Set environment variables
export SMTP_HOST="smtp.gmail.com"
export SMTP_USER="alerts@skinguard.com"
export SMTP_PASSWORD="your-password"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export PAGERDUTY_INTEGRATION_KEY="your-key"
export TWILIO_ACCOUNT_SID="your-sid"
export TWILIO_AUTH_TOKEN="your-token"
export TWILIO_FROM_NUMBER="+1234567890"
```

**Usage:**
```python
from deployment.monitoring.alerting import (
    AlertManager,
    alert_high_error_rate,
    alert_slow_response,
    alert_urgent_case_unreviewed
)

# Use convenience functions
alert_high_error_rate(0.08)  # 8% error rate
alert_slow_response(6500)  # 6.5 seconds
alert_urgent_case_unreviewed(3)  # 3 unreviewed cases

# Or use AlertManager directly
manager = AlertManager()
if manager.check_rule("High CPU Usage", 95):
    manager.trigger_alert("High CPU Usage", 95)
```

## Alert Rules

### Critical Alerts
- **High Error Rate:** Error rate > 5%
- **Database Connection Failure:** Database unavailable
- **AI Model Loading Failure:** Models failed to load
- **Service Unavailable:** Health check failures
- **Urgent Case Unreviewed:** Urgent medical case not reviewed in 24h
- **Suspicious Activity:** Security threat detected

### High Priority Alerts
- **Slow API Response Time:** Response time > 5 seconds
- **High Memory Usage:** Memory > 85%
- **High CPU Usage:** CPU > 90%
- **Failed Authentication Attempts:** > 10 failed logins in 5 minutes
- **External Service Failure:** Maps/Email/Video service errors

### Medium Priority Alerts
- **Slow AI Processing:** AI analysis > 10 seconds
- **High NSFW Rejection Rate:** > 20% rejection rate
- **Low Doctor Availability:** < 5 verified doctors
- **High Queue Length:** > 100 pending reports

## Log Aggregation

### CloudWatch (Production)

Logs are automatically sent to AWS CloudWatch in production.

**Log Groups:**
- `/aws/skinguard/production` - Application logs
- `/aws/skinguard/production/api` - API request logs
- `/aws/skinguard/production/ai` - AI processing logs
- `/aws/skinguard/production/security` - Security event logs

**Viewing Logs:**
```bash
# View recent logs
aws logs tail /aws/skinguard/production --follow

# Search logs
aws logs filter-log-events \
  --log-group-name /aws/skinguard/production \
  --filter-pattern "ERROR"

# Query with CloudWatch Insights
aws logs start-query \
  --log-group-name /aws/skinguard/production \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/'
```

### Local Development

In development, logs are written to console with DEBUG level.

```bash
# View logs in real-time
tail -f /var/log/skinguard/app.log

# View error logs
tail -f /var/log/skinguard/error.log

# View JSON logs
tail -f /var/log/skinguard/app.json | jq
```

## Performance Monitoring

### Metrics Tracked

1. **API Metrics:**
   - Request count
   - Response time (p50, p95, p99)
   - Error rate
   - Status code distribution

2. **AI Metrics:**
   - Processing time (Gatekeeper, Medical AI)
   - NSFW rejection rate
   - Model inference time
   - Queue length

3. **System Metrics:**
   - CPU usage
   - Memory usage
   - Disk space
   - Network I/O

4. **Business Metrics:**
   - Active users
   - Total screenings
   - Urgent cases
   - Doctor availability

### Viewing Metrics

**Sentry Performance:**
```
https://sentry.io/organizations/skinguard/performance/
```

**CloudWatch Metrics:**
```bash
# View API response time
aws cloudwatch get-metric-statistics \
  --namespace SkinGuard \
  --metric-name APIResponseTime \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

## Health Checks

Health check endpoints are monitored every 60 seconds:

- `GET /health` - Overall health
- `GET /health/db` - Database connectivity
- `GET /health/ai` - AI models status
- `GET /health/storage` - Storage availability

**Manual Health Check:**
```bash
curl https://api.skinguard.com/health
```

## Troubleshooting

### Sentry Not Capturing Errors

1. Check SENTRY_DSN is set correctly
2. Verify network connectivity to Sentry
3. Check Sentry quota limits
4. Review `before_send` filter in `sentry.config.py`

### Logs Not Appearing in CloudWatch

1. Verify AWS credentials are configured
2. Check IAM permissions for CloudWatch Logs
3. Verify log group exists
4. Check `watchtower` configuration in `logging.config.yaml`

### Alerts Not Sending

1. Check channel configuration in `alerts.config.yaml`
2. Verify environment variables are set
3. Check cooldown periods
4. Review alert manager logs
5. Test channel connectivity manually

### High Alert Volume

1. Adjust alert thresholds in `alerts.config.yaml`
2. Increase cooldown periods
3. Use maintenance windows during deployments
4. Review and consolidate similar alerts

## Best Practices

1. **Error Tracking:**
   - Always add context to errors (user_id, report_id)
   - Filter PII before sending to Sentry
   - Use appropriate severity levels
   - Add breadcrumbs for debugging

2. **Logging:**
   - Use structured logging with JSON format
   - Include relevant context in log messages
   - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Avoid logging sensitive data (passwords, tokens, medical images)

3. **Alerting:**
   - Set appropriate thresholds to avoid alert fatigue
   - Use cooldown periods to prevent spam
   - Configure escalation for critical alerts
   - Test alerts regularly
   - Document alert response procedures

4. **Performance:**
   - Monitor p95 and p99 response times, not just averages
   - Set up alerts for performance degradation
   - Track AI processing time separately
   - Monitor external service dependencies

## Integration with Backend

Add to your FastAPI application:

```python
# backend/app/main.py
from deployment.monitoring.sentry_config import init_sentry
from deployment.monitoring.logger import setup_logging, get_logger

# Initialize monitoring
init_sentry()
setup_logging()

# Get logger
logger = get_logger("app.api", logger_type="api")

# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.log_request(
        request.method,
        request.url.path,
        user_id=request.state.user_id if hasattr(request.state, 'user_id') else None
    )
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    logger.log_response(
        request.method,
        request.url.path,
        response.status_code,
        duration_ms
    )
    
    return response
```

## Maintenance

### Regular Tasks

1. **Daily:**
   - Review error logs
   - Check alert status
   - Monitor performance metrics

2. **Weekly:**
   - Review alert thresholds
   - Analyze performance trends
   - Check log storage usage

3. **Monthly:**
   - Review and update alert rules
   - Optimize log retention
   - Update monitoring dependencies
   - Test disaster recovery procedures

### Log Rotation

Logs are automatically rotated when they reach 10MB, keeping 10 backup files.

**Manual rotation:**
```bash
logrotate -f /etc/logrotate.d/skinguard
```

## Support

For monitoring issues:
- Email: devops@skinguard.com
- Slack: #skinguard-monitoring
- On-call: PagerDuty escalation
