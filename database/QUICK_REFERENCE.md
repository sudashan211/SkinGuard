# SkinGuard Database Quick Reference

## Common Database Operations

### Connection

```python
# Python (using psycopg2)
import psycopg2
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
```

```javascript
// JavaScript (using Supabase client)
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)
```

### User Management

```sql
-- Create a new patient profile
INSERT INTO profiles (id, email, full_name, role)
VALUES (auth.uid(), 'patient@example.com', 'John Doe', 'patient');

-- Create patient health data
INSERT INTO patient_data (user_id, age, skin_type, family_history)
VALUES (auth.uid(), 35, 'III', 'No family history of skin cancer');

-- Register a doctor
INSERT INTO profiles (id, email, full_name, role, verified)
VALUES (auth.uid(), 'doctor@example.com', 'Dr. Jane Smith', 'doctor', false);

INSERT INTO doctors (user_id, license_no, clinic_name, lat, lng, whatsapp_no)
VALUES (auth.uid(), 'MD12345', 'Skin Health Clinic', 40.7128, -74.0060, '+1234567890');

-- Verify a doctor (admin only)
UPDATE profiles
SET verified = true
WHERE id = 'doctor-uuid' AND role = 'doctor';
```

### Medical Reports

```sql
-- Create a medical report
INSERT INTO medical_reports (
    patient_id,
    image_url,
    ai_prediction,
    symptoms,
    status,
    risk_level,
    body_location
)
VALUES (
    auth.uid(),
    'https://storage.url/image.jpg',
    '{"predictions": [{"type": "melanoma", "probability": 0.75}], "hotspots": []}',
    '{"location": "left_arm", "sensations": ["itching"], "visual_changes": ["color"]}',
    'safe',
    'medium',
    'left_arm'
);

-- Get patient's report history
SELECT id, image_url, ai_prediction, status, risk_level, created_at
FROM medical_reports
WHERE patient_id = auth.uid()
ORDER BY created_at DESC;

-- Get urgent reports for doctors
SELECT mr.*, pd.age, pd.skin_type, p.full_name
FROM medical_reports mr
JOIN profiles p ON mr.patient_id = p.id
JOIN patient_data pd ON mr.patient_id = pd.user_id
WHERE mr.status = 'urgent'
ORDER BY mr.created_at DESC;
```

### Appointments

```sql
-- Create an appointment
INSERT INTO appointments (
    patient_id,
    doctor_id,
    report_id,
    scheduled_at,
    status,
    consultation_type
)
VALUES (
    auth.uid(),
    'doctor-uuid',
    'report-uuid',
    '2024-03-15 10:00:00+00',
    'pending',
    'video'
);

-- Get patient's appointments
SELECT a.*, d.clinic_name, p.full_name as doctor_name
FROM appointments a
JOIN doctors d ON a.doctor_id = d.id
JOIN profiles p ON d.user_id = p.id
WHERE a.patient_id = auth.uid()
ORDER BY a.scheduled_at DESC;

-- Get doctor's appointments
SELECT a.*, p.full_name as patient_name
FROM appointments a
JOIN profiles p ON a.patient_id = p.id
WHERE a.doctor_id IN (SELECT id FROM doctors WHERE user_id = auth.uid())
ORDER BY a.scheduled_at ASC;

-- Update appointment status
UPDATE appointments
SET status = 'completed'
WHERE id = 'appointment-uuid'
AND (patient_id = auth.uid() OR doctor_id IN (SELECT id FROM doctors WHERE user_id = auth.uid()));
```

### Doctor Locator

```sql
-- Find doctors within radius (using PostGIS)
SELECT 
    d.*,
    p.full_name,
    p.avatar_url,
    earth_distance(
        ll_to_earth(d.lat, d.lng),
        ll_to_earth(40.7128, -74.0060)  -- User's location
    ) / 1000 as distance_km
FROM doctors d
JOIN profiles p ON d.user_id = p.id
WHERE p.verified = true
AND earth_box(ll_to_earth(40.7128, -74.0060), 50000) @> ll_to_earth(d.lat, d.lng)  -- 50km radius
ORDER BY distance_km ASC
LIMIT 20;
```

### Reviews

```sql
-- Create a review
INSERT INTO reviews (patient_id, doctor_id, appointment_id, rating, review_text)
VALUES (
    auth.uid(),
    'doctor-uuid',
    'appointment-uuid',
    5,
    'Excellent consultation, very thorough and professional.'
);

-- Get doctor's reviews
SELECT r.*, p.full_name as patient_name
FROM reviews r
JOIN profiles p ON r.patient_id = p.id
WHERE r.doctor_id = 'doctor-uuid'
ORDER BY r.created_at DESC;

-- Get doctor's average rating
SELECT 
    d.id,
    d.average_rating,
    d.review_count
FROM doctors d
WHERE d.id = 'doctor-uuid';
```

### Notifications

```sql
-- Create a notification
INSERT INTO notifications (user_id, type, title, message, metadata)
VALUES (
    'user-uuid',
    'analysis_complete',
    'Analysis Complete',
    'Your skin analysis results are ready to view.',
    '{"report_id": "report-uuid"}'
);

-- Get user's unread notifications
SELECT *
FROM notifications
WHERE user_id = auth.uid()
AND read = false
ORDER BY created_at DESC;

-- Mark notification as read
UPDATE notifications
SET read = true
WHERE id = 'notification-uuid'
AND user_id = auth.uid();
```

### Audit Logs

```sql
-- Create an audit log entry
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, metadata, ip_address)
VALUES (
    auth.uid(),
    'view_report',
    'medical_report',
    'report-uuid',
    '{"timestamp": "2024-02-10T10:00:00Z"}',
    '192.168.1.1'::inet
);

-- Get user's audit trail
SELECT *
FROM audit_logs
WHERE user_id = auth.uid()
ORDER BY created_at DESC
LIMIT 100;

-- Get flagged content audit logs
SELECT *
FROM audit_logs
WHERE action = 'content_violation'
ORDER BY created_at DESC;
```

## Useful Queries

### Analytics

```sql
-- Daily active users
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users
FROM audit_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Total screenings by day
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_screenings
FROM medical_reports
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Most common cancer types detected
SELECT 
    ai_prediction->>'predictions'->0->>'type' as cancer_type,
    COUNT(*) as count
FROM medical_reports
WHERE status = 'safe'
GROUP BY cancer_type
ORDER BY count DESC;

-- Doctor performance metrics
SELECT 
    d.id,
    p.full_name,
    d.average_rating,
    d.review_count,
    COUNT(DISTINCT a.id) as total_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) as completed_appointments
FROM doctors d
JOIN profiles p ON d.user_id = p.id
LEFT JOIN appointments a ON d.id = a.doctor_id
WHERE p.verified = true
GROUP BY d.id, p.full_name, d.average_rating, d.review_count
ORDER BY d.average_rating DESC, d.review_count DESC;
```

### Data Cleanup

```sql
-- Delete old notifications (older than 90 days)
DELETE FROM notifications
WHERE created_at < NOW() - INTERVAL '90 days'
AND read = true;

-- Archive old audit logs (older than 1 year)
-- First create archive table, then move data
CREATE TABLE audit_logs_archive AS
SELECT * FROM audit_logs
WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM audit_logs
WHERE created_at < NOW() - INTERVAL '1 year';

-- Find orphaned records
SELECT mr.id, mr.image_url
FROM medical_reports mr
LEFT JOIN profiles p ON mr.patient_id = p.id
WHERE p.id IS NULL;
```

### Performance Monitoring

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- Check slow queries (requires pg_stat_statements extension)
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Backup and Restore

### Backup

```bash
# Full database backup
pg_dump -h db.your-project.supabase.co -U postgres -d postgres > backup_$(date +%Y%m%d).sql

# Backup specific tables
pg_dump -h db.your-project.supabase.co -U postgres -d postgres \
  -t profiles -t patient_data -t medical_reports > backup_core_$(date +%Y%m%d).sql

# Backup with compression
pg_dump -h db.your-project.supabase.co -U postgres -d postgres | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore

```bash
# Restore from backup
psql -h db.your-project.supabase.co -U postgres -d postgres < backup_20240210.sql

# Restore from compressed backup
gunzip -c backup_20240210.sql.gz | psql -h db.your-project.supabase.co -U postgres -d postgres
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
psql -h db.your-project.supabase.co -U postgres -d postgres -c "SELECT version();"

# Check if database is accepting connections
pg_isready -h db.your-project.supabase.co -p 5432
```

### RLS Issues

```sql
-- Disable RLS temporarily for debugging (admin only)
ALTER TABLE medical_reports DISABLE ROW LEVEL SECURITY;

-- Re-enable RLS
ALTER TABLE medical_reports ENABLE ROW LEVEL SECURITY;

-- Check current user
SELECT current_user, auth.uid();

-- Test policy
EXPLAIN (ANALYZE, VERBOSE) 
SELECT * FROM medical_reports WHERE patient_id = auth.uid();
```

### Performance Issues

```sql
-- Analyze table statistics
ANALYZE medical_reports;

-- Vacuum table
VACUUM ANALYZE medical_reports;

-- Reindex table
REINDEX TABLE medical_reports;

-- Check for missing indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
AND n_distinct > 100
AND correlation < 0.1;
```

## Security Best Practices

1. **Never expose service role key** - Use only in backend, never in frontend
2. **Use RLS policies** - Always rely on RLS for access control
3. **Validate input** - Use CHECK constraints and application validation
4. **Audit sensitive operations** - Log all access to medical data
5. **Encrypt at rest** - Ensure Supabase encryption is enabled
6. **Use HTTPS** - Always use TLS for connections
7. **Regular backups** - Automate daily backups
8. **Monitor access** - Review audit logs regularly
9. **Rotate credentials** - Change passwords and keys periodically
10. **Principle of least privilege** - Grant minimum necessary permissions

## References

- Supabase Documentation: https://supabase.com/docs
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- PostGIS Documentation: https://postgis.net/documentation/
- Requirements: 12.1, 12.4, 12.5
