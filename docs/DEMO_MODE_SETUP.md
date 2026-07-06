# SkinGuard Demo Mode Setup

## Overview
The SkinGuard application is now running in **DEMO MODE** for local development and testing without requiring a database connection.

## Servers Running

### Frontend Server
- **URL**: http://localhost:3000
- **Status**: ✅ Running (Process ID: 5)
- **Framework**: Vite + React + TypeScript

### Backend Server  
- **URL**: http://localhost:8000
- **Status**: ✅ Running (Process ID: 6)
- **Framework**: FastAPI + Python
- **Mode**: DEMO MODE (no database required)

## Demo Credentials

You can log in with these pre-configured demo accounts:

### Patient Account
- **Email**: `patient@demo.com`
- **Password**: `demo123`
- **Access**: Patient dashboard, skin screening, appointments

### Doctor Account
- **Email**: `doctor@demo.com`
- **Password**: `demo123`
- **Access**: Doctor dashboard, patient reports, appointments

### Admin Account
- **Email**: `admin@demo.com`
- **Password**: `demo123`
- **Access**: Admin dashboard, analytics, user management

## Features Available in Demo Mode

✅ **Working Features**:
- User authentication (login/logout)
- Role-based access control
- Dashboard navigation
- Analytics dashboard with demo data
- API health checks
- CORS properly configured

⚠️ **Limited Features** (demo data only):
- Analytics show static demo data
- No real database persistence
- No AI image analysis
- No email notifications

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

## Configuration Files

### Backend Configuration
- **File**: `backend/.env`
- **Demo Mode**: `DEMO_MODE=true`
- **CORS Origins**: `http://localhost:3000,http://localhost:5173`

### Frontend Configuration
- **File**: `frontend/.env`
- **API URL**: `VITE_API_URL=http://localhost:8000`

## Recent Fixes Applied

1. ✅ **Authentication Response Transformation**: Fixed frontend auth service to handle backend response format
2. ✅ **UserProfile Model**: Added `updated_at` field to demo user profiles
3. ✅ **Analytics Demo Mode**: Added demo data support for analytics dashboard
4. ✅ **Admin Service**: Fixed snake_case to camelCase transformation for analytics data
5. ✅ **CORS Configuration**: Properly configured to allow frontend requests

## Troubleshooting

### If you see CORS errors:
1. Check that both servers are running
2. Verify `backend/.env` has correct CORS_ORIGINS
3. Restart the backend server

### If login fails:
1. Use exact credentials listed above
2. Check browser console for errors
3. Verify backend is running on port 8000

### If analytics dashboard shows errors:
1. Clear browser cache and reload
2. Check that you're logged in as admin
3. Verify backend analytics endpoint is working: http://localhost:8000/api/admin/analytics

## Stopping the Servers

To stop the servers, you can:
1. Close the terminal windows
2. Or use Ctrl+C in each terminal
3. Or kill the processes by ID

## Next Steps for Production

To use this application in production, you'll need to:

1. **Set up Supabase Database**:
   - Create a new Supabase project
   - Update `backend/.env` with real Supabase credentials
   - Set `DEMO_MODE=false`

2. **Configure AI Models**:
   - Set up NSFW detection model
   - Configure medical AI models (Swin Transformer + EfficientNet)

3. **Email Service**:
   - Configure SMTP settings for email notifications

4. **Security**:
   - Generate secure JWT secret key
   - Enable HTTPS/TLS
   - Configure proper CORS origins for production domain

## Support

For issues or questions, check:
- Backend logs in the terminal running the backend server
- Frontend console in browser DevTools
- API documentation at http://localhost:8000/api/docs
