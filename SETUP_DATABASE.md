# 🗄️ Database Setup Instructions

## Problem
Your Supabase database is empty and needs tables to be created.

## Solution
Run the SQL script to create all required tables.

## Steps

### 1. Open Supabase SQL Editor

1. Go to https://supabase.com/dashboard
2. Click on your "SkinGuard Project"
3. Click on "SQL Editor" in the left sidebar (or go to https://supabase.com/dashboard/project/fqvxrlltwymecsugfzcg/sql)

### 2. Run the Setup Script

1. Click "New Query" button
2. Copy the entire content from `database_setup.sql` file
3. Paste it into the SQL editor
4. Click "Run" button (or press Ctrl+Enter)
5. Wait for it to complete (should take a few seconds)
6. You should see: "Database setup complete! All tables created successfully."

### 3. Verify Tables Were Created

1. Click on "Table Editor" in the left sidebar
2. You should see these tables:
   - profiles
   - patient_data
   - doctors
   - medical_reports
   - appointments
   - reviews
   - audit_logs

### 4. Test Account Creation

1. Go back to your app: http://localhost:3000
2. Try creating an account again
3. It should work now! ✅

## What the Script Does

The script creates 7 tables:

1. **profiles** - User accounts (email, role, etc.)
2. **patient_data** - Patient health profiles
3. **doctors** - Doctor profiles and clinic info
4. **medical_reports** - AI screening reports
5. **appointments** - Appointment bookings
6. **reviews** - Doctor reviews
7. **audit_logs** - System logs and metrics

Plus indexes for better performance.

## Troubleshooting

### Error: "relation already exists"
- This is OK! It means some tables already exist
- The script uses `IF NOT EXISTS` so it won't break

### Error: "permission denied"
- Make sure you're logged into the correct Supabase account
- Make sure you're in the correct project

### Tables not showing up
- Refresh the page
- Check you're in the "public" schema
- Try running the script again

## After Setup

Once tables are created:
1. Backend will connect successfully
2. You can create accounts
3. Data will persist permanently
4. All features will work

## Quick Copy-Paste

The SQL script is in the file: `database_setup.sql`

Just copy everything from that file and paste it into Supabase SQL Editor!
