# SkinGuard System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                    http://localhost:3000                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             │ (API calls via VITE_API_URL)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                       │
│                         Port: 3000                               │
├─────────────────────────────────────────────────────────────────┤
│  • React 18 + TypeScript                                         │
│  • TailwindCSS for styling                                       │
│  • React Query for data fetching                                │
│  • React Router for navigation                                  │
│  • Environment: VITE_API_URL=http://localhost:8001              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API Calls
                             │ (JSON over HTTP)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│                         Port: 8001                               │
├─────────────────────────────────────────────────────────────────┤
│  • FastAPI framework                                             │
│  • Uvicorn ASGI server                                          │
│  • JWT authentication                                            │
│  • Role-based access control                                    │
│  • File upload handling                                          │
│  • API Documentation: /docs                                      │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             │ SQL Queries                   │ Model Inference
             │                               │
             ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   PostgreSQL Database    │    │      AI Model            │
│      Port: 5432          │    │    (TensorFlow)          │
├──────────────────────────┤    ├──────────────────────────┤
│  • Database: skinguard   │    │  • Skin cancer detection │
│  • User: postgres        │    │  • 96.95% accuracy       │
│  • Password: 12345       │    │  • 7 cancer types        │
│  • Tables:               │    │  • Image preprocessing   │
│    - profiles            │    │  • Prediction output     │
│    - doctors             │    └──────────────────────────┘
│    - reports             │
│    - appointments        │
│    - audit_logs          │
│    - etc.                │
└──────────────────────────┘
```

## Port Configuration

```
┌─────────────────────────────────────────────────────────────┐
│                    PORT ALLOCATION                           │
├──────────────┬──────────────────────────────────────────────┤
│   Port 3000  │  Frontend (Vite Dev Server)                  │
│   Port 8001  │  Backend API (FastAPI/Uvicorn)               │
│   Port 5432  │  PostgreSQL Database                         │
└──────────────┴──────────────────────────────────────────────┘
```

## Data Flow

### 1. User Login Flow
```
User Browser
    │
    │ POST /api/auth/login
    │ { email, password }
    ▼
Backend API
    │
    │ Query database
    ▼
PostgreSQL
    │
    │ Return user data
    ▼
Backend API
    │
    │ Generate JWT token
    │ Return { access_token, user }
    ▼
Frontend
    │
    │ Store token in localStorage
    │ Redirect to dashboard
    ▼
User Dashboard
```

### 2. Skin Screening Flow
```
User uploads image
    │
    │ POST /api/reports
    │ FormData: { image, symptoms, location }
    ▼
Backend API
    │
    ├─▶ Save image to uploads/
    │
    ├─▶ Preprocess image
    │   │
    │   ▼
    │   AI Model (TensorFlow)
    │   │
    │   │ Predict cancer type
    │   │ Calculate probabilities
    │   │
    │   └─▶ Return predictions
    │
    ├─▶ Calculate risk level
    │
    └─▶ Save to database
        │
        ▼
    PostgreSQL (reports table)
        │
        │ Return report ID
        ▼
    Frontend
        │
        │ Show results
        │ Display predictions
        │ Suggest next steps
        ▼
    User sees report
```

### 3. Doctor Review Flow
```
Doctor logs in
    │
    │ GET /api/doctors/pending-reports
    ▼
Backend API
    │
    │ Query reports for doctor's patients
    ▼
PostgreSQL
    │
    │ Return pending reports
    ▼
Frontend (Doctor Dashboard)
    │
    │ Doctor reviews report
    │ Adds consultation notes
    │
    │ PUT /api/reports/{id}
    │ { consultation_notes, status }
    ▼
Backend API
    │
    │ Update report
    ▼
PostgreSQL
    │
    │ Report updated
    ▼
Patient notified
```

## Authentication Flow

```
┌──────────────┐
│ User Login   │
└──────┬───────┘
       │
       │ POST /api/auth/login
       ▼
┌──────────────────────┐
│ Backend validates    │
│ email + password     │
└──────┬───────────────┘
       │
       │ bcrypt.verify()
       ▼
┌──────────────────────┐
│ Generate JWT token   │
│ with user_id + role  │
└──────┬───────────────┘
       │
       │ Return token
       ▼
┌──────────────────────┐
│ Frontend stores      │
│ token in localStorage│
└──────┬───────────────┘
       │
       │ All subsequent requests
       │ include: Authorization: Bearer <token>
       ▼
┌──────────────────────┐
│ Backend verifies     │
│ token on each request│
└──────────────────────┘
```

## Role-Based Access Control

```
┌─────────────────────────────────────────────────────────────┐
│                         ROLES                                │
├─────────────┬───────────────────────────────────────────────┤
│   Patient   │  • Upload images                              │
│             │  • View own reports                           │
│             │  • Book appointments                          │
│             │  • View own profile                           │
├─────────────┼───────────────────────────────────────────────┤
│   Doctor    │  • View patient reports (with appointments)   │
│             │  • Add consultation notes                     │
│             │  • Manage appointments                        │
│             │  • Update own profile                         │
├─────────────┼───────────────────────────────────────────────┤
│   Admin     │  • All patient/doctor permissions             │
│             │  • User management                            │
│             │  • System health monitoring                   │
│             │  • Audit logs access                          │
│             │  • Compliance reports                         │
└─────────────┴───────────────────────────────────────────────┘
```

## Database Schema (Simplified)

```
┌─────────────────┐
│    profiles     │
├─────────────────┤
│ id (PK)         │
│ email           │
│ password_hash   │
│ full_name       │
│ role            │◄────┐
│ verified        │     │
│ status          │     │
└─────────────────┘     │
                        │
┌─────────────────┐     │
│    doctors      │     │
├─────────────────┤     │
│ id (PK)         │     │
│ user_id (FK)    │─────┘
│ clinic_name     │
│ specialization  │
│ whatsapp_no     │
└─────────────────┘
         │
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  appointments   │     │    reports      │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ patient_id (FK) │     │ user_id (FK)    │
│ doctor_id (FK)  │─────│ image_url       │
│ scheduled_at    │     │ predictions     │
│ status          │     │ risk_level      │
└─────────────────┘     │ status          │
                        │ consultation_   │
                        │   notes         │
                        └─────────────────┘
```

## File Structure

```
SkinGuard/
│
├── backend/                    # Backend API (Port 8001)
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── database.py        # Database connection
│   │   ├── postgres_db.py     # PostgreSQL adapter
│   │   ├── auth.py            # Authentication logic
│   │   ├── models.py          # Pydantic models
│   │   ├── routers/           # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── doctors.py
│   │   │   ├── patients.py
│   │   │   └── admin.py
│   │   └── ai_model/          # AI model files
│   ├── .env                   # Backend config
│   └── requirements.txt
│
├── frontend/                   # Frontend app (Port 3000)
│   ├── src/
│   │   ├── pages/             # React pages
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   ├── utils/             # Utilities
│   │   └── App.tsx
│   ├── .env                   # Frontend config
│   └── package.json
│
├── uploads/                    # Uploaded images
│
├── docs/                       # Documentation
│   ├── PORT_CONFIGURATION.md
│   ├── AI_MODEL_STATUS.md
│   └── PRODUCTION_DEPLOYMENT_GUIDE.md
│
├── database_setup.sql          # Database schema
├── SERVER_STARTUP.md           # Startup guide
├── START_HERE.md               # Quick reference
├── STARTUP_CHECKLIST.md        # Startup checklist
└── README.md                   # Project overview
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:12345@localhost:5432/skinguard
USE_REAL_AI=true
API_PORT=8001
SECRET_KEY=<generated>
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8001
VITE_GOOGLE_MAPS_API_KEY=<your_key>
```

## API Endpoints Overview

```
Authentication
├── POST   /api/auth/signup
├── POST   /api/auth/login
└── GET    /api/auth/me

Patients
├── GET    /api/reports
├── POST   /api/reports
├── GET    /api/reports/{id}
└── GET    /api/appointments

Doctors
├── GET    /api/doctors/nearby
├── GET    /api/doctors/pending-reports
├── PUT    /api/reports/{id}
└── GET    /api/doctors/appointments

Admin
├── GET    /api/admin/users
├── GET    /api/admin/system/health
├── GET    /api/admin/audit/logs
└── POST   /api/admin/audit/compliance-report
```

---

**Remember**: 
- Backend on port **8001** (not 8000!)
- Frontend on port **3000**
- PostgreSQL on port **5432**
- All API calls use `VITE_API_URL` environment variable
