# SkinGuard - Working Credentials & Setup

## System Status
✅ Backend: Running on http://localhost:8001
✅ Frontend: Running on http://localhost:3000
✅ Database: PostgreSQL (local) via pgAdmin
✅ AI Model: Real model (96.95% accuracy)

## Working User Accounts

### Patient Account
- **Email:** `sudashanrao0702@gmail.com`
- **Password:** `Password123`
- **Role:** Patient
- **Features:** Upload images, view reports, book appointments

### Doctor Account #1
- **Email:** `doctor@skinguard.com`
- **Password:** `Doctor123`
- **Role:** Doctor
- **Features:** Review reports, manage appointments, consultations

### Doctor Account #2 (Dr. Pratap)
- **Email:** `pratap@gmail.com`
- **Password:** Use the password you set during signup
- **Role:** Doctor
- **Note:** Run `add_pratap_doctor_profile.sql` in pgAdmin to complete setup

## Password Requirements
When creating new accounts, passwords MUST have:
- ✅ At least 8 characters
- ✅ At least one UPPERCASE letter
- ✅ At least one lowercase letter
- ✅ At least one digit (0-9)

**Valid examples:** `Password123`, `Doctor456`, `Patient789`
**Invalid examples:** `password` (no uppercase/digit), `PASSWORD` (no lowercase/digit)

## Common Issues & Solutions

### Issue: 401/403 Errors
**Solution:** You're not logged in. Go to http://localhost:3000/login and log in with valid credentials.

### Issue: 422 on Signup
**Solution:** Password doesn't meet requirements. Use format like `YourName123`

### Issue: Doctor not showing in dropdown
**Solution:** 
1. Check if doctor profile exists in `doctors` table (run SQL query)
2. If missing, run the appropriate SQL script to create doctor profile
3. Refresh the page

### Issue: 404 on /api/doctors/profile
**Solution:** Doctor profile missing in `doctors` table. Run the SQL script to create it.

## SQL Scripts to Run (if needed)

### 1. Add password_hash column (if missing)
```sql
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS password_hash TEXT;
```

### 2. Add ip_address column to audit_logs (if missing)
```sql
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45);
```

### 3. Create doctor profile for Dr. Pratap
Run: `add_pratap_doctor_profile.sql`

### 4. Check all doctors
```sql
SELECT d.id, p.email, p.full_name, d.specialization, d.clinic_name
FROM doctors d
JOIN profiles p ON d.user_id = p.id;
```

## How to Use the System

### As a Patient:
1. Log in with patient credentials
2. Go to "Upload Image" to analyze skin lesions
3. View results in "My Reports"
4. Book appointments with doctors
5. View health profile and manage privacy settings

### As a Doctor:
1. Log in with doctor credentials
2. View pending reports from patients
3. Review AI analysis results
4. Provide consultations
5. Manage appointments

## Database Connection
- **Host:** localhost
- **Port:** 5432
- **Database:** skinguard
- **Username:** postgres
- **Password:** 12345

## Troubleshooting

If you see many 403 errors:
1. Clear browser cache and cookies
2. Log out completely
3. Close all browser tabs
4. Log in again with valid credentials

If backend won't start:
1. Check if port 8001 is available
2. Check PostgreSQL is running
3. Verify DATABASE_URL in backend/.env

If frontend won't start:
1. Check if port 3000 is available
2. Run `npm install` in frontend directory
3. Check VITE_API_URL in frontend/.env
