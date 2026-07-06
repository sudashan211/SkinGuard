# SkinGuard Production Deployment Guide

## Overview

This guide provides step-by-step procedures for deploying SkinGuard to production. Follow each section carefully and verify completion before proceeding to the next step.

## Pre-Deployment Checklist

- [ ] All 93 property tests passing
- [ ] Security audit completed (A- rating achieved)
- [ ] Production environment configured
- [ ] SSL certificates installed and verified
- [ ] All API keys and secrets stored in secure vault
- [ ] Database backups configured
- [ ] Monitoring and alerting configured
- [ ] Rollback procedures tested
- [ ] Team briefed on launch procedures

## Deployment Steps

### Step 1: Database Migration

**Objective**: Deploy production database schema and seed data

```bash
# 1. Connect to production Supabase instance
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-service-role-key"

# 2. Run database migrations
cd backend
python scripts/migrate_database.py --env production

# 3. Verify all tables created
python scripts/verify_schema.py

# 4. Seed initial data (admin accounts, educational content)
python scripts/seed_production.py

# 5. Verify RLS policies active
python scripts/verify_rls.py
```

**Verification**:
- [ ] All 8 tables created (profiles, patient_data, doctors, medical_reports, appointments, reviews, notifications, audit_logs)
- [ ] All indexes created successfully
- [ ] RLS policies active on all tables
- [ ] Admin account accessible
- [ ] Educational content loaded

**Rollback**: If verification fails, run `python scripts/rollback_migration.py`

---

### Step 2: AI Model Deployment

**Objective**: Deploy AI models to production inference servers

```bash
# 1. Upload models to production storage
cd backend/models
aws s3 sync . s3://skinguard-models-prod/ --exclude "*.pyc"

# 2. Deploy model inference service
cd ../inference
docker build -t skinguard-inference:latest .
docker tag skinguard-inference:latest your-registry/skinguard-inference:v1.0.0
docker push your-registry/skinguard-inference:v1.0.0

# 3. Deploy to Kubernetes/ECS
kubectl apply -f k8s/inference-deployment.yaml
# OR
aws ecs update-service --cluster skinguard-prod --service inference --force-new-deployment

# 4. Verify model loading
curl https://api.skinguard.com/health/models
```

**Verification**:
- [ ] NSFW detector loaded successfully
- [ ] Swin Transformer loaded successfully
- [ ] EfficientNet-B7 loaded successfully
- [ ] Test inference completes in <5 seconds
- [ ] GPU utilization normal (<80%)

**Rollback**: Revert to previous container version using `kubectl rollout undo` or ECS console

---

### Step 3: Backend API Deployment

**Objective**: Deploy FastAPI backend to production

```bash
# 1. Build backend container
cd backend
docker build -t skinguard-api:latest .
docker tag skinguard-api:latest your-registry/skinguard-api:v1.0.0
docker push your-registry/skinguard-api:v1.0.0

# 2. Update environment variables
kubectl create secret generic api-secrets \
  --from-literal=SUPABASE_URL=$SUPABASE_URL \
  --from-literal=SUPABASE_KEY=$SUPABASE_KEY \
  --from-literal=JWT_SECRET=$JWT_SECRET \
  --from-literal=SENDGRID_API_KEY=$SENDGRID_API_KEY \
  --from-literal=GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY

# 3. Deploy API service
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/api-ingress.yaml

# 4. Wait for rollout completion
kubectl rollout status deployment/skinguard-api

# 5. Verify API health
curl https://api.skinguard.com/health
```

**Verification**:
- [ ] API health check returns 200 OK
- [ ] All endpoints responding
- [ ] Database connection successful
- [ ] Redis cache connected
- [ ] External services accessible (SendGrid, Google Maps)
- [ ] Rate limiting active
- [ ] CORS configured correctly

**Rollback**: `kubectl rollout undo deployment/skinguard-api`

---

### Step 4: Frontend Deployment

**Objective**: Deploy React frontend to CDN

```bash
# 1. Build production frontend
cd frontend
npm run build

# 2. Verify build output
ls -lh dist/
# Should see index.html, assets/, and service worker

# 3. Deploy to Vercel/Netlify
vercel --prod
# OR
netlify deploy --prod --dir=dist

# 4. Verify deployment
curl https://skinguard.com
curl https://skinguard.com/manifest.json
```

**Verification**:
- [ ] Homepage loads successfully
- [ ] All assets loading from CDN
- [ ] Service worker registered
- [ ] PWA installable
- [ ] API calls reaching backend
- [ ] Google Maps loading
- [ ] All routes accessible

**Rollback**: Revert to previous deployment in Vercel/Netlify dashboard

---

### Step 5: Configure CDN and Caching

**Objective**: Optimize content delivery and caching

```bash
# 1. Configure CloudFront distribution
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json

# 2. Update DNS records
# Point skinguard.com to CloudFront distribution
# Point api.skinguard.com to API load balancer

# 3. Configure cache policies
# - Static assets: 1 year cache
# - API responses: No cache
# - Images: 30 days cache

# 4. Enable compression
# - Gzip for text assets
# - WebP for images
```

**Verification**:
- [ ] DNS propagated (check with `dig skinguard.com`)
- [ ] SSL certificate valid
- [ ] Cache headers correct
- [ ] Compression enabled
- [ ] CDN serving content globally

---

### Step 6: Enable Monitoring and Alerting

**Objective**: Activate production monitoring

```bash
# 1. Configure Sentry for error tracking
export SENTRY_DSN="your-sentry-dsn"
# Already configured in application code

# 2. Set up CloudWatch/Datadog dashboards
# Import dashboard configurations from monitoring/dashboards/

# 3. Configure alerts
# - API response time > 5s
# - Error rate > 1%
# - Database connection failures
# - AI inference failures
# - Disk space < 20%

# 4. Set up log aggregation
# Configure log shipping to CloudWatch/ELK
```

**Verification**:
- [ ] Sentry receiving error reports
- [ ] Metrics flowing to monitoring system
- [ ] Dashboards displaying data
- [ ] Test alerts triggering correctly
- [ ] Logs searchable

---

### Step 7: Configure External Services

**Objective**: Activate third-party integrations

**Email Service (SendGrid)**:
```bash
# 1. Verify SendGrid API key
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"personalizations":[{"to":[{"email":"test@example.com"}]}],"from":{"email":"noreply@skinguard.com"},"subject":"Test","content":[{"type":"text/plain","value":"Test"}]}'

# 2. Configure email templates
# Upload templates to SendGrid dashboard

# 3. Set up domain authentication
# Add DNS records for SPF, DKIM, DMARC
```

**Google Maps API**:
```bash
# 1. Verify API key restrictions
# - HTTP referrers: https://skinguard.com/*
# - API restrictions: Maps JavaScript API, Geocoding API

# 2. Test API access
curl "https://maps.googleapis.com/maps/api/geocode/json?address=test&key=$GOOGLE_MAPS_API_KEY"
```

**WhatsApp Business API**:
```bash
# 1. Verify WhatsApp Business account active
# 2. Test message template approval
# 3. Configure webhook for message status
```

**Video Consultation (Twilio/Agora)**:
```bash
# 1. Verify video API credentials
# 2. Test room creation
# 3. Configure recording settings (if required)
# 4. Verify HIPAA compliance settings
```

**Verification**:
- [ ] Test email sent successfully
- [ ] Google Maps loading on frontend
- [ ] WhatsApp links working
- [ ] Video rooms creating successfully
- [ ] All API quotas sufficient

---

### Step 8: Security Hardening

**Objective**: Final security checks

```bash
# 1. Verify SSL/TLS configuration
ssllabs-scan --quiet skinguard.com

# 2. Check security headers
curl -I https://skinguard.com | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)"

# 3. Verify rate limiting
# Run load test to trigger rate limits

# 4. Test authentication flows
# Verify JWT expiration, refresh tokens

# 5. Verify NSFW filter active
# Upload test images

# 6. Check database encryption
# Verify AES-256 encryption on Supabase Storage
```

**Verification**:
- [ ] SSL Labs rating A or higher
- [ ] Security headers present
- [ ] Rate limiting working
- [ ] Authentication secure
- [ ] NSFW filter blocking inappropriate content
- [ ] Data encrypted at rest and in transit

---

### Step 9: Performance Optimization

**Objective**: Ensure optimal performance

```bash
# 1. Run Lighthouse audit
lighthouse https://skinguard.com --output html --output-path ./lighthouse-report.html

# 2. Test API response times
# Use load testing tool (k6, Artillery)
k6 run load-tests/api-test.js

# 3. Test AI inference speed
# Should complete in <5 seconds for 95th percentile

# 4. Verify database query performance
# Check slow query logs

# 5. Test on 3G connection
# Use Chrome DevTools network throttling
```

**Verification**:
- [ ] Lighthouse score >90 for Performance
- [ ] API p95 response time <2s
- [ ] AI inference p95 <5s
- [ ] Database queries optimized
- [ ] App usable on 3G

---

### Step 10: Final Smoke Tests

**Objective**: Verify all critical paths

**Patient Journey**:
```bash
# 1. Register new patient account
# 2. Complete health profile
# 3. Upload skin lesion image
# 4. Verify AI analysis completes
# 5. View results with disclaimer
# 6. Find nearby doctor on map
# 7. Book appointment
# 8. Receive confirmation email
```

**Doctor Journey**:
```bash
# 1. Register doctor account
# 2. Wait for admin verification (or manually verify)
# 3. View pending reports
# 4. Review patient report
# 5. Add consultation notes
# 6. View appointments
# 7. Join video consultation
```

**Admin Journey**:
```bash
# 1. Login as admin
# 2. Verify pending doctor
# 3. Review flagged content
# 4. View analytics dashboard
# 5. Edit Skin-Wiki content
```

**Verification**:
- [ ] All patient flows working
- [ ] All doctor flows working
- [ ] All admin flows working
- [ ] Emails sending correctly
- [ ] Notifications appearing
- [ ] No console errors

---

## Post-Deployment Verification

### Automated Health Checks

Run the automated health check suite:

```bash
cd scripts
python production_health_check.py --env production
```

This script verifies:
- API endpoints responding
- Database connectivity
- AI models loaded
- External services accessible
- SSL certificates valid
- Monitoring active

### Manual Verification

- [ ] Visit https://skinguard.com and verify homepage loads
- [ ] Register test patient account
- [ ] Upload test image and verify analysis
- [ ] Check monitoring dashboard for metrics
- [ ] Verify error tracking in Sentry
- [ ] Test mobile responsiveness
- [ ] Test PWA installation
- [ ] Verify all languages working

---

## Rollback Procedures

If critical issues are discovered post-deployment:

### Full Rollback

```bash
# 1. Revert frontend
vercel rollback
# OR
netlify rollback

# 2. Revert backend API
kubectl rollout undo deployment/skinguard-api

# 3. Revert AI inference service
kubectl rollout undo deployment/skinguard-inference

# 4. Revert database (if migrations ran)
python scripts/rollback_migration.py --to-version <previous-version>

# 5. Update DNS if needed
# Point to previous infrastructure

# 6. Notify team and stakeholders
```

### Partial Rollback

If only specific components need rollback:

```bash
# Rollback frontend only
vercel rollback

# Rollback API only
kubectl rollout undo deployment/skinguard-api

# Rollback AI service only
kubectl rollout undo deployment/skinguard-inference
```

---

## Deployment Timeline

**Estimated Total Time**: 4-6 hours

- Step 1 (Database): 30 minutes
- Step 2 (AI Models): 45 minutes
- Step 3 (Backend API): 45 minutes
- Step 4 (Frontend): 30 minutes
- Step 5 (CDN): 30 minutes
- Step 6 (Monitoring): 30 minutes
- Step 7 (External Services): 45 minutes
- Step 8 (Security): 30 minutes
- Step 9 (Performance): 30 minutes
- Step 10 (Smoke Tests): 45 minutes

**Recommended Deployment Window**: Off-peak hours (e.g., Sunday 2 AM - 8 AM)

---

## Team Responsibilities

**DevOps Engineer**:
- Execute deployment steps 1-6
- Configure monitoring and alerting
- Manage infrastructure

**Backend Developer**:
- Verify API deployment
- Test AI inference
- Monitor error logs

**Frontend Developer**:
- Verify frontend deployment
- Test user flows
- Check browser compatibility

**QA Engineer**:
- Execute smoke tests
- Verify all critical paths
- Document any issues

**Product Manager**:
- Coordinate deployment timing
- Communicate with stakeholders
- Approve go-live decision

---

## Emergency Contacts

**On-Call Rotation**:
- Primary: [Name] - [Phone] - [Email]
- Secondary: [Name] - [Phone] - [Email]
- Escalation: [Name] - [Phone] - [Email]

**External Support**:
- Supabase Support: support@supabase.io
- Vercel Support: support@vercel.com
- SendGrid Support: support@sendgrid.com
- Google Cloud Support: [Your support plan]

---

## Success Criteria

Deployment is considered successful when:

- [ ] All health checks passing
- [ ] All smoke tests passing
- [ ] No critical errors in logs
- [ ] Monitoring showing normal metrics
- [ ] All external services working
- [ ] Test users can complete full journeys
- [ ] Performance metrics within targets
- [ ] Security audit passing

**Sign-off Required From**:
- [ ] DevOps Lead
- [ ] Backend Lead
- [ ] Frontend Lead
- [ ] QA Lead
- [ ] Product Manager

---

## Next Steps

After successful deployment:

1. Monitor system for first 24 hours closely
2. Review metrics and logs daily for first week
3. Collect user feedback
4. Plan first patch release for any minor issues
5. Schedule post-launch retrospective

---

*Document Version: 1.0*  
*Last Updated: Launch Day*  
*Owner: DevOps Team*
