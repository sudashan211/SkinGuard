# SkinGuard Production Deployment Checklist

This checklist ensures all steps are completed before and after production deployment.

## Pre-Deployment Checklist

### 1. Code Quality ✓
- [ ] All tests passing (unit, property, integration, E2E)
- [ ] Code review completed
- [ ] No critical security vulnerabilities
- [ ] Linting passes with no errors
- [ ] Code coverage > 80%
- [ ] All 93 property tests implemented and passing

### 2. Environment Configuration ✓
- [ ] Production environment variables configured
- [ ] `.env.production` file created and validated
- [ ] All API keys and secrets rotated for production
- [ ] JWT secret key is strong (32+ characters)
- [ ] Database credentials secured
- [ ] SSL/TLS certificates obtained

### 3. Database Setup ✓
- [ ] Production Supabase instance created
- [ ] Database migrations tested
- [ ] Row Level Security (RLS) policies enabled
- [ ] PostGIS extension installed
- [ ] Database backups configured
- [ ] Connection pooling configured

### 4. Backend Preparation ✓
- [ ] AI models downloaded and tested
- [ ] Model inference tested on production hardware
- [ ] API endpoints documented
- [ ] Rate limiting configured
- [ ] CORS settings configured for production domain
- [ ] Error tracking (Sentry) configured
- [ ] Logging configured

### 5. Frontend Preparation ✓
- [ ] Production build tested locally
- [ ] Environment variables set for build
- [ ] Google Maps API key configured
- [ ] PWA manifest configured
- [ ] Service worker tested
- [ ] Bundle size optimized (< 500KB gzipped)

### 6. External Services ✓
- [ ] Supabase production project created
- [ ] SendGrid/AWS SES configured for email
- [ ] Twilio/Agora configured for video calls
- [ ] Google Maps API enabled and billed
- [ ] CloudFront CDN configured
- [ ] Domain DNS configured

### 7. Security ✓
- [ ] Security audit completed
- [ ] HTTPS/TLS enabled
- [ ] Security headers configured
- [ ] NSFW filter tested and calibrated
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] CSRF protection enabled
- [ ] File upload validation tested
- [ ] Audit logging enabled

### 8. Monitoring & Alerting ✓
- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring configured
- [ ] Log aggregation configured
- [ ] Uptime monitoring configured
- [ ] Alert thresholds configured
- [ ] On-call rotation established

### 9. Documentation ✓
- [ ] API documentation up to date
- [ ] Deployment guide reviewed
- [ ] Runbook created for common issues
- [ ] Architecture diagrams updated
- [ ] User guides prepared

### 10. Backup & Recovery ✓
- [ ] Database backup strategy configured
- [ ] Backup restoration tested
- [ ] Disaster recovery plan documented
- [ ] Rollback procedure documented

---

## Deployment Steps

### Phase 1: Database Deployment
```bash
# 1. Run database migrations
cd database/migrations
psql $DATABASE_URL -f 001_initial_schema.sql
psql $DATABASE_URL -f 002_indexes_and_rls.sql
# ... run all migrations

# 2. Verify database setup
python tests/verify_database_setup.py
```
- [ ] Migrations completed successfully
- [ ] Database verification passed

### Phase 2: Backend Deployment

#### Option A: AWS Lambda
```bash
cd deployment/aws/lambda
serverless deploy --stage production
```
- [ ] Lambda function deployed
- [ ] API Gateway configured
- [ ] Custom domain configured
- [ ] Health check passing

#### Option B: EC2
```bash
cd deployment/aws/ec2
./setup-ec2.sh
```
- [ ] EC2 instance configured
- [ ] Application deployed
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] Health check passing

#### Option C: Docker
```bash
cd deployment/docker
docker-compose -f docker-compose.prod.yml up -d
```
- [ ] Containers running
- [ ] Health checks passing
- [ ] Logs accessible

### Phase 3: Frontend Deployment

#### Option A: Vercel
```bash
cd deployment/vercel
vercel --prod
```
- [ ] Frontend deployed to Vercel
- [ ] Custom domain configured
- [ ] Environment variables set
- [ ] Build successful

#### Option B: Netlify
```bash
cd deployment/netlify
netlify deploy --prod
```
- [ ] Frontend deployed to Netlify
- [ ] Custom domain configured
- [ ] Environment variables set
- [ ] Build successful

### Phase 4: CDN Configuration
```bash
# Configure CloudFront for image storage
aws cloudfront create-distribution --config file://cloudfront-config.json
```
- [ ] CloudFront distribution created
- [ ] Origin configured (Supabase Storage)
- [ ] Cache behaviors configured
- [ ] SSL certificate attached
- [ ] DNS updated

---

## Post-Deployment Checklist

### 1. Smoke Tests ✓
- [ ] Backend health endpoint responding
- [ ] Frontend loading correctly
- [ ] User registration working
- [ ] User login working
- [ ] Image upload working
- [ ] AI analysis working
- [ ] Doctor locator working
- [ ] Appointment booking working
- [ ] Email notifications working
- [ ] Video consultation working

### 2. Performance Tests ✓
- [ ] API response times < 500ms (95th percentile)
- [ ] AI analysis completes < 10s
- [ ] Frontend loads < 3s
- [ ] Lighthouse score > 90
- [ ] No memory leaks detected
- [ ] Database queries optimized

### 3. Security Verification ✓
- [ ] HTTPS working correctly
- [ ] Security headers present
- [ ] CORS configured correctly
- [ ] Rate limiting working
- [ ] NSFW filter blocking inappropriate content
- [ ] Authentication working
- [ ] Authorization working
- [ ] Audit logs being created

### 4. Monitoring Verification ✓
- [ ] Error tracking receiving events
- [ ] Performance metrics being collected
- [ ] Logs being aggregated
- [ ] Alerts configured and tested
- [ ] Uptime monitoring active

### 5. User Acceptance Testing ✓
- [ ] Patient flow tested end-to-end
- [ ] Doctor flow tested end-to-end
- [ ] Admin flow tested end-to-end
- [ ] Mobile experience tested
- [ ] Cross-browser testing completed
- [ ] Accessibility testing completed

### 6. Documentation Updates ✓
- [ ] Deployment date recorded
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Known issues documented
- [ ] Team notified

### 7. Backup Verification ✓
- [ ] First backup completed
- [ ] Backup restoration tested
- [ ] Backup schedule verified

---

## Rollback Procedure

If issues are detected post-deployment:

### Backend Rollback

#### Lambda:
```bash
serverless rollback --stage production --timestamp TIMESTAMP
```

#### EC2:
```bash
ssh ubuntu@ec2-host
cd /opt/skinguard
git checkout PREVIOUS_COMMIT
supervisorctl restart skinguard-backend
```

#### Docker:
```bash
docker-compose -f docker-compose.prod.yml down
docker pull skinguard/backend:PREVIOUS_TAG
docker-compose -f docker-compose.prod.yml up -d
```

### Frontend Rollback

#### Vercel:
```bash
vercel rollback
```

#### Netlify:
```bash
netlify rollback
```

### Database Rollback
```bash
# Restore from backup
psql $DATABASE_URL < backup_TIMESTAMP.sql
```

---

## Post-Deployment Monitoring (First 24 Hours)

### Hour 1
- [ ] Monitor error rates
- [ ] Check API response times
- [ ] Verify all services healthy
- [ ] Review logs for errors

### Hour 6
- [ ] Check user registrations
- [ ] Verify AI analyses completing
- [ ] Check email delivery
- [ ] Review performance metrics

### Hour 24
- [ ] Generate deployment report
- [ ] Review all metrics
- [ ] Document any issues
- [ ] Plan fixes for issues

---

## Success Criteria

Deployment is considered successful when:

1. ✓ All smoke tests passing
2. ✓ Error rate < 1%
3. ✓ API response time < 500ms (95th percentile)
4. ✓ Frontend load time < 3s
5. ✓ AI analysis time < 10s
6. ✓ No critical errors in logs
7. ✓ All monitoring systems active
8. ✓ User flows working end-to-end
9. ✓ Security scans passing
10. ✓ Team notified and trained

---

## Emergency Contacts

- **Technical Lead**: [Name] - [Email] - [Phone]
- **DevOps**: [Name] - [Email] - [Phone]
- **On-Call Engineer**: [Name] - [Email] - [Phone]
- **Product Manager**: [Name] - [Email] - [Phone]

---

## Useful Commands

### Check Backend Health
```bash
curl https://api.skinguard.com/health
```

### Check Frontend
```bash
curl https://skinguard.com
```

### View Backend Logs (EC2)
```bash
ssh ubuntu@ec2-host
tail -f /var/log/skinguard/error.log
```

### View Backend Logs (Lambda)
```bash
aws logs tail /aws/lambda/skinguard-backend-production-api --follow
```

### View Docker Logs
```bash
docker logs -f skinguard-backend-prod
```

### Check Database Connection
```bash
psql $DATABASE_URL -c "SELECT 1"
```

### Run Database Backup
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

**Deployment Date**: _________________  
**Deployed By**: _________________  
**Version**: _________________  
**Sign-off**: _________________
