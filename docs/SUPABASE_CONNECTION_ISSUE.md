# Supabase Connection Issue - RESOLVED

## Problem

When trying to create an account in production mode, you get:
- Error: "Invalid request data" (422 Unprocessable Entity)
- Backend logs show: `httpx.ConnectError: [Errno 11001] getaddrinfo failed`

## Root Cause

Your computer cannot resolve the Supabase hostname: `fqvxrlltwymecsuqfzcg.supabase.co`

This means the backend cannot connect to your Supabase database.

## Possible Reasons

1. **Supabase Project Paused**: Free tier projects pause after inactivity
2. **DNS Issue**: Your DNS cannot resolve the Supabase domain
3. **Network/Firewall**: Something is blocking the connection
4. **Project Deleted**: The Supabase project might have been deleted

## Solutions

### Solution 1: Check Supabase Project Status (RECOMMENDED)

1. Go to https://supabase.com/dashboard
2. Login to your account
3. Check if your project `fqvxrlltwymecsuqfzcg` exists
4. If it's paused, click "Resume Project"
5. Wait for it to become active
6. Try creating an account again

### Solution 2: Create New Supabase Project

If your project was deleted or doesn't exist:

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Create a new project
4. Copy the new credentials:
   - Project URL
   - Anon Key
   - Service Role Key
5. Update `backend/.env` with new credentials
6. Set up database tables (see below)

### Solution 3: Use Demo Mode (Temporary)

If you just want to test the system without database:

1. Edit `backend/.env`
2. Change `DEMO_MODE=false` to `DEMO_MODE=true`
3. Restart backend server
4. You can create accounts and test features
5. Data will be in-memory (lost on restart)

## Database Setup (If Creating New Project)

Your Supabase database needs these tables:

### 1. profiles
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  role TEXT NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
  verified BOOLEAN DEFAULT FALSE,
  avatar_url TEXT,
  language_preference TEXT DEFAULT 'en',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. patient_data
```sql
CREATE TABLE patient_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  age INTEGER CHECK (age >= 1 AND age <= 120),
  skin_type TEXT CHECK (skin_type IN ('I', 'II', 'III', 'IV', 'V', 'VI')),
  family_history TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. doctors
```sql
CREATE TABLE doctors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  license_no TEXT UNIQUE NOT NULL,
  clinic_name TEXT,
  lat DOUBLE PRECISION,
  lng DOUBLE PRECISION,
  whatsapp_no TEXT,
  specialization TEXT,
  bio TEXT,
  education TEXT,
  certifications TEXT,
  languages TEXT,
  clinic_hours TEXT,
  average_rating DOUBLE PRECISION DEFAULT 0,
  review_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. medical_reports
```sql
CREATE TABLE medical_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  ai_prediction JSONB,
  symptoms TEXT,
  status TEXT CHECK (status IN ('safe', 'urgent', 'flagged')),
  risk_level TEXT,
  body_location TEXT,
  consultation_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 5. appointments
```sql
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  doctor_id UUID REFERENCES doctors(id) ON DELETE CASCADE,
  report_id UUID REFERENCES medical_reports(id) ON DELETE SET NULL,
  scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
  consultation_type TEXT CHECK (consultation_type IN ('in_person', 'video')),
  video_room_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 6. reviews
```sql
CREATE TABLE reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  doctor_id UUID REFERENCES doctors(id) ON DELETE CASCADE,
  appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  flagged BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Quick Fix: Use Demo Mode

For immediate testing, switch to demo mode:

```bash
# Edit backend/.env
DEMO_MODE=true

# Restart backend
# Stop current server (Ctrl+C)
# Start: uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Recommended Action

**Check your Supabase dashboard first!** Your project might just be paused and needs to be resumed.

1. Visit: https://supabase.com/dashboard
2. Find project: `fqvxrlltwymecsuqfzcg`
3. Resume if paused
4. Verify it's active
5. Try again

If the project doesn't exist, you'll need to create a new one and update the credentials in `backend/.env`.
