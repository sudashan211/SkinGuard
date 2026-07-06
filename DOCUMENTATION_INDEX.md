# 📚 SkinGuard Documentation Index

Complete guide to all documentation files in this project.

## 🚀 Quick Start (Read These First!)

### 1. START_HERE.md
**Purpose**: Quick reference card for starting servers  
**When to use**: Every time you start the application  
**Contains**:
- Copy-paste commands for starting servers
- Login credentials
- Important URLs
- Port numbers

### 2. SERVER_STARTUP.md
**Purpose**: Complete startup guide with troubleshooting  
**When to use**: First time setup or when having issues  
**Contains**:
- Detailed startup instructions
- Pre-startup checklist
- Environment variable configuration
- Common issues and solutions
- User accounts reference

### 3. STARTUP_CHECKLIST.md
**Purpose**: Step-by-step checklist for starting servers  
**When to use**: Print this or keep it open while starting  
**Contains**:
- Pre-startup checks
- Startup commands
- Post-startup verification
- Port verification
- Quick fixes

## 📖 Core Documentation

### 4. README.md
**Purpose**: Project overview and introduction  
**When to use**: Understanding what SkinGuard is  
**Contains**:
- Project description
- Features overview
- Technology stack
- Installation instructions
- Quick start guide

### 5. SYSTEM_ARCHITECTURE.md
**Purpose**: Visual system architecture and data flow  
**When to use**: Understanding how the system works  
**Contains**:
- System diagrams
- Data flow charts
- Database schema
- API endpoints overview
- File structure

### 6. TROUBLESHOOTING.md
**Purpose**: Solutions to common problems  
**When to use**: When something isn't working  
**Contains**:
- Backend issues
- Frontend issues
- Database issues
- Port conflicts
- Authentication problems
- Admin dashboard fixes

## 🔧 Technical Documentation

### 7. docs/PORT_CONFIGURATION.md
**Purpose**: Detailed port and network configuration  
**When to use**: Understanding port setup or changing ports  
**Contains**:
- Port allocation (3000, 8001, 5432)
- CORS settings
- Network configuration
- Firewall rules
- Development vs production setup

### 8. docs/AI_MODEL_STATUS.md
**Purpose**: AI model information and status  
**When to use**: Understanding the AI capabilities  
**Contains**:
- Model accuracy (96.95%)
- Supported cancer types
- Model architecture
- Performance metrics

### 9. docs/PRODUCTION_DEPLOYMENT_GUIDE.md
**Purpose**: Guide for deploying to production  
**When to use**: When deploying to live server  
**Contains**:
- Production setup
- Security considerations
- Deployment steps
- Environment configuration

### 10. docs/SUPABASE_CONNECTION_ISSUE.md
**Purpose**: Migration from Supabase to PostgreSQL  
**When to use**: Historical reference  
**Contains**:
- Why we switched from Supabase
- Migration process
- PostgreSQL setup

## 🗄️ Database Documentation

### 11. SETUP_DATABASE.md
**Purpose**: Database setup instructions  
**When to use**: First time database setup  
**Contains**:
- PostgreSQL installation
- Database creation
- Table setup
- Initial data

### 12. database_setup.sql
**Purpose**: Complete database schema  
**When to use**: Creating or resetting database  
**Contains**:
- All table definitions
- Indexes
- Constraints
- Initial setup

### 13. add_password_hash_column.sql
**Purpose**: Add password_hash column to profiles  
**When to use**: Database migration (already applied)  
**Contains**:
- ALTER TABLE statement for password_hash

### 14. fix_audit_logs_ip_address.sql
**Purpose**: Fix audit logs IP address column  
**When to use**: Database migration (already applied)  
**Contains**:
- ALTER TABLE statement for ip_address

## 📝 Scripts and Utilities

### 15. create_admin.py
**Purpose**: Create admin user account  
**When to use**: Creating new admin accounts  
**Usage**: `python create_admin.py`

### 16. verify_all_doctors.py
**Purpose**: Set all doctors to verified status  
**When to use**: Bulk verify doctors  
**Usage**: `python verify_all_doctors.py`

### 17. fix_missing_whatsapp.py
**Purpose**: Add default WhatsApp numbers to doctors  
**When to use**: Fix missing WhatsApp data  
**Usage**: `python fix_missing_whatsapp.py`

## 📋 Spec Files (.kiro/specs/)

### 18. derman-ai-skin-screening/
**Purpose**: Original project specification  
**Contains**:
- requirements.md - Project requirements
- design.md - System design
- tasks.md - Implementation tasks

### 19. fix-find-doctor-errors/
**Purpose**: Bug fix specification  
**Contains**:
- bugfix.md - Bug description
- design.md - Fix design
- tasks.md - Fix tasks

## 🎯 Documentation Usage Guide

### For First Time Setup
1. Read **README.md** - Understand the project
2. Read **SERVER_STARTUP.md** - Complete setup guide
3. Follow **SETUP_DATABASE.md** - Setup database
4. Use **STARTUP_CHECKLIST.md** - Start servers
5. Keep **START_HERE.md** - For future reference

### For Daily Development
1. Open **START_HERE.md** - Quick commands
2. Use **STARTUP_CHECKLIST.md** - Verify everything
3. Refer to **TROUBLESHOOTING.md** - If issues arise

### For Understanding System
1. Read **SYSTEM_ARCHITECTURE.md** - System overview
2. Check **docs/PORT_CONFIGURATION.md** - Network setup
3. Review **docs/AI_MODEL_STATUS.md** - AI capabilities

### For Troubleshooting
1. Check **TROUBLESHOOTING.md** - Common issues
2. Review **SERVER_STARTUP.md** - Startup problems
3. Verify **docs/PORT_CONFIGURATION.md** - Port issues

## 📊 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| START_HERE.md | ✅ Current | April 3, 2026 |
| SERVER_STARTUP.md | ✅ Current | April 3, 2026 |
| STARTUP_CHECKLIST.md | ✅ Current | April 3, 2026 |
| README.md | ✅ Current | April 3, 2026 |
| SYSTEM_ARCHITECTURE.md | ✅ Current | April 3, 2026 |
| TROUBLESHOOTING.md | ✅ Current | April 3, 2026 |
| PORT_CONFIGURATION.md | ✅ Current | April 3, 2026 |
| SETUP_DATABASE.md | ✅ Current | March 2026 |
| database_setup.sql | ✅ Current | March 2026 |

## 🔍 Quick Search

### Looking for...
- **Startup commands?** → START_HERE.md
- **Port numbers?** → START_HERE.md or PORT_CONFIGURATION.md
- **Login credentials?** → START_HERE.md or SERVER_STARTUP.md
- **Error solutions?** → TROUBLESHOOTING.md
- **System overview?** → SYSTEM_ARCHITECTURE.md
- **Database setup?** → SETUP_DATABASE.md
- **API endpoints?** → SYSTEM_ARCHITECTURE.md
- **Environment variables?** → SERVER_STARTUP.md
- **Port conflicts?** → TROUBLESHOOTING.md
- **Admin dashboard issues?** → TROUBLESHOOTING.md

## 📌 Important Reminders

### Critical Information
- **Backend Port**: 8001 (NOT 8000!)
- **Frontend Port**: 3000
- **Database Port**: 5432
- **Database Name**: skinguard
- **Database User**: postgres
- **Database Password**: 12345

### Environment Files
- `backend/.env` - Backend configuration
- `frontend/.env` - Frontend configuration (VITE_API_URL)

### Key Commands
```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Frontend
cd frontend
npm run dev
```

## 🆘 Need Help?

### Step-by-Step Troubleshooting
1. Check **START_HERE.md** - Verify basic setup
2. Review **STARTUP_CHECKLIST.md** - Follow checklist
3. Read **TROUBLESHOOTING.md** - Find your issue
4. Check **SERVER_STARTUP.md** - Detailed guide
5. Review **SYSTEM_ARCHITECTURE.md** - Understand system

### Common Issues Quick Links
- Port 8000 errors → TROUBLESHOOTING.md → Admin Dashboard Issues
- Connection refused → TROUBLESHOOTING.md → Frontend Issues
- Database errors → TROUBLESHOOTING.md → Database Issues
- Login problems → TROUBLESHOOTING.md → Authentication Issues

---

**Remember**: Always start with START_HERE.md! 🚀

**Last Updated**: April 3, 2026  
**Documentation Version**: 1.0.0
