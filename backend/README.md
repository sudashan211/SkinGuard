# SkinGuard Backend API

FastAPI backend for the SkinGuard AI Skin Cancer Screening Platform.

## Features

- ✅ User authentication with JWT tokens
- ✅ Role-based access control (patient, doctor, admin)
- ✅ Password hashing with bcrypt
- ✅ Supabase integration for database and auth
- ✅ RESTful API endpoints
- ✅ Automatic API documentation (Swagger/ReDoc)
- ✅ CORS configuration
- ✅ Error handling and validation

## Requirements

- Python 3.10+
- Supabase project (database must be set up first)
- PostgreSQL 14+ (provided by Supabase)

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32
```

Generate a secure JWT secret key:

```bash
openssl rand -hex 32
```

### 3. Verify Database Setup

Ensure the database is set up first (Task 1 must be complete):

```bash
cd ../database
python scripts/verify_setup.py
```

### 4. Run the Server

```bash
cd backend
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Authentication

#### POST /api/auth/signup
Register a new user with role assignment.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "patient"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "patient",
  "verified": false,
  "language_preference": "en",
  "created_at": "2024-02-10T12:00:00Z",
  "updated_at": "2024-02-10T12:00:00Z"
}
```

#### POST /api/auth/login
Authenticate user and get JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "patient",
    "verified": false
  }
}
```

#### POST /api/auth/logout
Logout current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Successfully logged out",
  "user_id": "uuid"
}
```

#### GET /api/auth/me
Get current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "patient",
  "verified": false,
  "language_preference": "en",
  "created_at": "2024-02-10T12:00:00Z",
  "updated_at": "2024-02-10T12:00:00Z"
}
```

#### POST /api/auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Health Check

#### GET /api/health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-02-10T12:00:00Z",
  "version": "1.0.0"
}
```

## Authentication

All protected endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Expiration

- Access tokens expire after 30 minutes
- Refresh tokens expire after 7 days
- Use the `/api/auth/refresh` endpoint to get new tokens

## Role-Based Access Control

The API implements role-based access control with three roles:

1. **Patient** - Can access diagnostic features and doctor locator
2. **Doctor** - Can access patient reports (requires verification)
3. **Admin** - Can access all features including moderation

### Dependencies

Use these dependencies in route handlers to enforce role-based access:

```python
from app.dependencies import (
    get_current_user,           # Any authenticated user
    get_current_patient,        # Patient role required
    get_current_doctor,         # Doctor role required
    get_current_verified_doctor,# Verified doctor required
    get_current_admin           # Admin role required
)

@router.get("/patient-only")
async def patient_endpoint(user: dict = Depends(get_current_patient)):
    # Only patients can access this
    pass

@router.get("/verified-doctor-only")
async def doctor_endpoint(user: dict = Depends(get_current_verified_doctor)):
    # Only verified doctors can access this
    pass
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details",
    "timestamp": "2024-02-10T12:00:00Z",
    "request_id": "uuid"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR` (422) - Invalid request data
- `AUTH_ERROR` (401) - Authentication failed
- `INSUFFICIENT_PERMISSIONS` (403) - Insufficient permissions
- `NOT_FOUND` (404) - Resource not found
- `INTERNAL_SERVER_ERROR` (500) - Server error

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Supabase client
│   ├── models.py            # Pydantic models
│   ├── auth.py              # Authentication utilities
│   ├── dependencies.py      # FastAPI dependencies
│   └── routers/
│       ├── __init__.py
│       └── auth.py          # Authentication routes
├── requirements.txt
├── .env.example
└── README.md
```

### Adding New Endpoints

1. Create a new router file in `app/routers/`
2. Define your routes using FastAPI decorators
3. Include the router in `app/main.py`
4. Use dependencies for authentication and authorization

Example:

```python
# app/routers/patients.py
from fastapi import APIRouter, Depends
from app.dependencies import get_current_patient

router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("/profile")
async def get_patient_profile(user: dict = Depends(get_current_patient)):
    return {"message": "Patient profile"}
```

```python
# app/main.py
from app.routers import auth, patients

app.include_router(auth.router)
app.include_router(patients.router)
```

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Run property-based tests:

```bash
pytest tests/property/ -v
```

## Security

- Passwords are hashed using bcrypt
- JWT tokens are signed with HS256
- All database connections use TLS/SSL
- Row Level Security (RLS) enforced at database level
- CORS configured for allowed origins only
- Service role key never exposed to clients

## Troubleshooting

### Connection Issues

```bash
# Test Supabase connection
python -c "from app.database import supabase; print(supabase.table('profiles').select('count').execute())"
```

### Token Issues

- Ensure JWT_SECRET_KEY is set and consistent
- Check token expiration times
- Verify token format (Bearer <token>)

### Permission Issues

- Check user role in database
- Verify doctor verification status
- Check RLS policies in Supabase

## References

- Requirements: 1.1, 1.2, 1.4, 1.5, 1.6, 6.5, 6.6
- Design Document: `.kiro/specs/derman-ai-skin-screening/design.md`
- FastAPI Docs: https://fastapi.tiangolo.com/
- Supabase Docs: https://supabase.com/docs
