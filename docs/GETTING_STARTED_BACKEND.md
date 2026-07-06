# Getting Started with SkinGuard Backend

Quick start guide for running the SkinGuard authentication backend.

## Prerequisites

✅ Task 1 complete (Database setup)  
✅ Python 3.10 or higher installed  
✅ Supabase project created and configured  

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
# Get these from your Supabase project settings
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Generate a secure secret key
JWT_SECRET_KEY=your-secret-key-here
```

**Generate JWT Secret Key:**

```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### 3. Verify Database Connection

```bash
cd ../database
python scripts/verify_setup.py
```

If this fails, make sure you completed Task 1 (Database Setup).

### 4. Start the Backend Server

```bash
cd ../backend
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Test the API

**Option 1: Use the Browser**

Open http://localhost:8000/api/docs to see the interactive API documentation.

**Option 2: Use the Test Script**

```bash
# In a new terminal (keep the server running)
cd backend
python test_auth_manual.py
```

**Option 3: Use curl**

```bash
# Health check
curl http://localhost:8000/api/health

# Register a user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "role": "patient"
  }'
```

## API Endpoints

### Authentication

- **POST /api/auth/signup** - Register new user
- **POST /api/auth/login** - Login and get tokens
- **POST /api/auth/logout** - Logout user
- **GET /api/auth/me** - Get current user profile
- **POST /api/auth/refresh** - Refresh access token

### Health

- **GET /api/health** - Check API health
- **GET /** - API information

## Common Issues

### Port Already in Use

```bash
# Change the port in .env
API_PORT=8001

# Or set it when running
API_PORT=8001 python -m app.main
```

### Database Connection Failed

1. Check your Supabase credentials in `.env`
2. Verify database is set up (run `database/scripts/verify_setup.py`)
3. Check your internet connection
4. Verify Supabase project is active

### Import Errors

```bash
# Make sure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

### JWT Secret Key Error

Make sure you generated and added a JWT_SECRET_KEY to your `.env` file:

```bash
openssl rand -hex 32
```

## Next Steps

1. ✅ Backend is running
2. ⏭️ Test the authentication endpoints
3. ⏭️ Integrate with frontend
4. ⏭️ Continue with Task 3: Patient Profile Management

## Documentation

- **API Docs**: http://localhost:8000/api/docs
- **Backend README**: `backend/README.md`
- **Task Summary**: `TASK_2_COMPLETION_SUMMARY.md`
- **Design Document**: `.kiro/specs/derman-ai-skin-screening/design.md`

## Support

If you encounter issues:

1. Check the troubleshooting section in `backend/README.md`
2. Verify all prerequisites are met
3. Check the server logs for error messages
4. Ensure database setup is complete

---

**Ready to build!** 🚀

The authentication backend is now running and ready for integration with the frontend or further backend development.
