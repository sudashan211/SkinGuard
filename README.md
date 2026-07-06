# SkinGuard - AI-Powered Skin Cancer Detection Platform

SkinGuard is a comprehensive healthcare platform that uses advanced AI to detect skin cancer from images, connecting patients with dermatologists for professional consultation.

## 🚀 Quick Start

**IMPORTANT**: Read these documents before starting:
1. **START_HERE.md** - Quick reference for server startup
2. **SERVER_STARTUP.md** - Complete startup guide with troubleshooting

### Start Servers

```bash
# Terminal 1 - Backend (Port 8001)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend (Port 3000)
cd frontend
npm run dev
```

### Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/docs
- Database: PostgreSQL on localhost:5432

## 📋 Features

### For Patients
- AI-powered skin lesion analysis (96.95% accuracy)
- Upload images and get instant risk assessment
- Book appointments with verified dermatologists
- Track screening history and reports
- Secure medical data storage

### For Doctors
- Review patient reports with AI predictions
- Manage appointments and consultations
- Add professional notes to patient reports
- View pending cases requiring attention
- Access patient medical history

### For Administrators
- System health monitoring
- User management (patients, doctors, admins)
- Audit logs and security events
- Compliance reporting
- Service status tracking

## 🏗️ Architecture

### Technology Stack
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **Backend**: FastAPI (Python), Uvicorn
- **Database**: PostgreSQL (local)
- **AI Model**: TensorFlow/Keras (96.95% accuracy)
- **Authentication**: JWT tokens

### System Components
```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   Frontend  │─────▶│   Backend   │─────▶│  PostgreSQL  │
│  (Port 3000)│      │  (Port 8001)│      │  (Port 5432) │
└─────────────┘      └─────────────┘      └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  AI Model   │
                     │  (TensorFlow)│
                     └─────────────┘
```

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- pgAdmin 4 (recommended)

### Backend Setup
```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Setup database
psql -U postgres -d skinguard -f ../database_setup.sql
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup
1. Install PostgreSQL and pgAdmin
2. Create database: `skinguard`
3. Run setup script: `database_setup.sql`
4. Verify tables are created

## 🔐 User Accounts

### Admin
- Email: admin@skinguard.com
- Password: Admin123

### Patient
- Email: sudashanrao0702@gmail.com
- Password: Password123

### Doctors
- doctor@skinguard.com / Doctor123
- kesava@gmaill.com / Kesava55

## 📖 Documentation

### Essential Documents
- **START_HERE.md** - Quick reference guide
- **SERVER_STARTUP.md** - Complete startup instructions
- **docs/PORT_CONFIGURATION.md** - Port and network configuration
- **SETUP_DATABASE.md** - Database setup guide

### Technical Documentation
- **docs/AI_MODEL_STATUS.md** - AI model information
- **docs/PRODUCTION_DEPLOYMENT_GUIDE.md** - Production deployment
- **docs/SUPABASE_CONNECTION_ISSUE.md** - Migration from Supabase

## 🔧 Configuration

### Port Configuration
- Backend API: **8001** (NOT 8000!)
- Frontend: **3000**
- PostgreSQL: **5432**

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:12345@localhost:5432/skinguard
USE_REAL_AI=true
API_PORT=8001
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8001
VITE_GOOGLE_MAPS_API_KEY=your_key_here
```

## 🧪 Testing

### Test Backend
```bash
curl http://localhost:8001/docs
```

### Test Frontend
Open http://localhost:3000 in browser

### Test Database
```bash
psql -U postgres -d skinguard -c "SELECT version();"
```

## 🐛 Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify port 8001 is not in use
- Check DATABASE_URL in .env

### Frontend shows connection errors
- Verify backend is running on port 8001
- Check VITE_API_URL in frontend/.env
- Hard refresh browser (Ctrl+Shift+R)

### Database connection errors
- Verify PostgreSQL service is running
- Check credentials: postgres/12345
- Ensure database 'skinguard' exists

**See SERVER_STARTUP.md for complete troubleshooting guide**

## 📊 Project Status

- ✅ PostgreSQL database integration
- ✅ AI model (96.95% accuracy)
- ✅ Patient screening workflow
- ✅ Doctor consultation system
- ✅ Admin dashboard
- ✅ Authentication & authorization
- ✅ Audit logging
- ✅ System health monitoring

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Audit logging for all actions
- Secure file upload handling
- SQL injection prevention
- CORS configuration

## 📝 License

Proprietary - All rights reserved

## 👥 Support

For issues or questions:
1. Check SERVER_STARTUP.md for common issues
2. Review docs/ folder for detailed documentation
3. Check backend logs for error messages

---

**Last Updated**: April 3, 2026  
**Version**: 1.0.0 (PostgreSQL Production Mode)  
**Status**: Production Ready ✅
