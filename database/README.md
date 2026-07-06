# SkinGuard Database Setup

This directory contains the database schema, migrations, and configuration for the SkinGuard AI Skin Cancer Screening Platform.

## Overview

The database uses **Supabase** (PostgreSQL) with the following features:
- Row Level Security (RLS) for data access control
- PostGIS extension for geographic queries
- JSONB for flexible AI prediction storage
- Automated triggers for data consistency
- Storage buckets for medical images with AES-256 encryption

## Requirements

- Supabase project (create at https://supabase.com)
- PostgreSQL 14+ (provided by Supabase)
- PostGIS extension (for doctor location queries)

## Database Schema

### Tables

1. **profiles** - User authentication and profile information
2. **patient_data** - Patient health profiles (age, skin type, family history)
3. **doctors** - Doctor registration and verification data
4. **medical_reports** - AI analysis results and patient reports
5. **appointments** - Patient-doctor appointment scheduling
6. **reviews** - Doctor ratings and reviews
7. **notifications** - User notifications and alerts
8. **audit_logs** - Security and compliance audit trail

### Key Features

- **Referential Integrity**: Foreign key constraints ensure data consistency (Requirements 12.4, 12.5)
- **Cascading Deletes**: Patient data is automatically removed when accounts are deleted
- **Automatic Timestamps**: `updated_at` fields are automatically maintained
- **Rating Calculations**: Doctor ratings are automatically recalculated when reviews change
- **Geographic Indexing**: PostGIS spatial indexes for efficient doctor location queries

## Setup Instructions

### 1. Create Supabase Project

1. Go to https://supabase.com and create a new project
2. Note your project URL and API keys
3. Wait for the project to be fully provisioned

### 2. Run Migrations

Execute the migration files in order:

```bash
# Option 1: Using Supabase CLI
supabase db push

# Option 2: Using psql
psql -h db.your-project.supabase.co -U postgres -d postgres -f database/migrations/001_initial_schema.sql
psql -h db.your-project.supabase.co -U postgres -d postgres -f database/migrations/002_rls_policies.sql
psql -h db.your-project.supabase.co -U postgres -d postgres -f database/migrations/003_storage_setup.sql

# Option 3: Using Supabase Dashboard
# Copy and paste each migration file into the SQL Editor and execute
```

### 3. Configure Storage Bucket

Create the medical images storage bucket:

**Via Supabase Dashboard:**
1. Go to Storage section
2. Click "Create bucket"
3. Name: `medical-images`
4. Public: `false` (private)
5. File size limit: `10MB`
6. Allowed MIME types: `image/jpeg, image/png, image/jpg`

**Via Supabase CLI:**
```bash
supabase storage create medical-images --public false
```

### 4. Configure Environment Variables

Create a `.env` file in your backend directory:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres
```

### 5. Verify Setup

Run the verification script to ensure everything is configured correctly:

```bash
python database/scripts/verify_setup.py
```

## Row Level Security (RLS)

All tables have RLS enabled with the following access patterns:

### Profiles
- Users can view and update their own profile
- Admins can view and update all profiles

### Patient Data
- Patients can view and update their own data
- Doctors can view patient data for their appointments
- Admins can view all patient data

### Medical Reports
- Patients can view their own reports
- Verified doctors can view safe/urgent reports
- Admins can view all reports

### Appointments
- Patients can view and manage their appointments
- Doctors can view and update their appointments
- Admins can view all appointments

### Reviews
- Anyone can view reviews (public)
- Patients can create reviews for completed appointments
- Doctors can flag inappropriate reviews
- Admins can moderate all reviews

### Storage (Medical Images)
- Patients can upload and view their own images
- Verified doctors can view images from accessible reports
- Admins can view and delete all images

## Indexes

Performance indexes are created for:
- User lookups by email and role
- Report queries by patient, status, and date
- Appointment queries by patient, doctor, and date
- Geographic queries for doctor location (PostGIS)
- Notification queries by user and read status

## Triggers

Automated triggers maintain data consistency:
- `updated_at` timestamps are automatically updated
- Doctor ratings are recalculated when reviews change
- Audit logs are created for sensitive operations

## Backup and Recovery

### Automated Backups
Supabase provides automated daily backups. Configure retention in project settings.

### Manual Backup
```bash
# Backup entire database
pg_dump -h db.your-project.supabase.co -U postgres -d postgres > backup.sql

# Backup specific table
pg_dump -h db.your-project.supabase.co -U postgres -d postgres -t medical_reports > reports_backup.sql
```

### Restore
```bash
psql -h db.your-project.supabase.co -U postgres -d postgres < backup.sql
```

## Maintenance

### Cleanup Orphaned Images
Run periodically to remove images not referenced in medical_reports:
```sql
SELECT cleanup_orphaned_images();
```

### Cleanup Deleted Account Data
Run after 30-day grace period for deleted accounts:
```sql
SELECT cleanup_deleted_account_images();
```

### Vacuum and Analyze
Optimize database performance:
```sql
VACUUM ANALYZE;
```

## Security Considerations

1. **Encryption at Rest**: All data is encrypted using AES-256 (Supabase default)
2. **Encryption in Transit**: All connections use TLS/SSL
3. **Row Level Security**: Fine-grained access control on all tables
4. **Audit Logging**: All sensitive operations are logged
5. **Service Role Key**: Keep service role key secure, never expose to client

## Monitoring

Monitor database health using Supabase Dashboard:
- Query performance
- Connection pool usage
- Storage usage
- Error rates

## Troubleshooting

### Connection Issues
```bash
# Test connection
psql -h db.your-project.supabase.co -U postgres -d postgres -c "SELECT version();"
```

### RLS Issues
```sql
-- Check if RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- View policies for a table
SELECT * FROM pg_policies WHERE tablename = 'medical_reports';
```

### Performance Issues
```sql
-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan ASC;
```

## Migration History

| Version | File | Description | Date |
|---------|------|-------------|------|
| 001 | 001_initial_schema.sql | Initial database schema with all tables | 2024-02-10 |
| 002 | 002_rls_policies.sql | Row Level Security policies | 2024-02-10 |
| 003 | 003_storage_setup.sql | Storage bucket configuration | 2024-02-10 |

## Support

For issues or questions:
1. Check Supabase documentation: https://supabase.com/docs
2. Review migration files for schema details
3. Check audit_logs table for security events
4. Contact development team

## References

- Requirements: 12.1, 12.4, 12.5
- Design Document: `.kiro/specs/derman-ai-skin-screening/design.md`
- Supabase Docs: https://supabase.com/docs/guides/database
- PostGIS Docs: https://postgis.net/documentation/
