# SkinGuard - Getting Started

Welcome to the SkinGuard AI Skin Cancer Screening Platform! This guide will help you get the database set up and ready for development.

## 🚀 Quick Start (5 minutes)

### Step 1: Create Supabase Project
1. Go to https://supabase.com
2. Sign up or log in
3. Click "New Project"
4. Choose a name: `skinguard-ai`
5. Set a strong database password
6. Select region closest to you
7. Wait for project to be created (~2 minutes)

### Step 2: Get Your Credentials
1. In Supabase Dashboard, go to **Settings** → **API**
2. Copy these values:
   - Project URL
   - `anon` `public` key
   - `service_role` `secret` key
3. Go to **Settings** → **Database**
4. Copy the connection string

### Step 3: Configure Environment
```bash
# Copy the template
cp database/.env.example .env

# Edit .env and paste your credentials
# Replace the placeholder values with your actual credentials
```

Your `.env` should look like:
```env
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmnop.supabase.co:5432/postgres
```

### Step 4: Run Setup
```bash
# Install Python dependencies
pip install -r database/requirements.txt

# Run automated setup
cd database
bash scripts/setup.sh
```

**Windows users**: Use `python` instead of `python3` and run migrations manually via Supabase Dashboard.

### Step 5: Create Storage Bucket
1. In Supabase Dashboard, go to **Storage**
2. Click **Create bucket**
3. Name: `medical-images`
4. Public: **OFF** (keep it private)
5. File size limit: `10485760` (10MB)
6. Allowed MIME types: `image/jpeg, image/png, image/jpg`
7. Click **Create**

### Step 6: Verify Setup
```bash
python database/scripts/verify_setup.py
```

You should see all checks passing! ✅

## 📖 What's Next?

### For Backend Developers
1. **Start the backend server**: See `GETTING_STARTED_BACKEND.md`
2. Test the authentication endpoints
3. Review the API documentation at http://localhost:8000/api/docs
4. Continue with Task 3: Patient Profile Management
5. Use the design document: `.kiro/specs/derman-ai-skin-screening/design.md`

### For Frontend Developers
1. Backend authentication API is ready!
2. Review the API endpoints in `backend/README.md`
3. Set up React + Vite project
4. Install dependencies: `npm install @supabase/supabase-js axios`
5. Implement authentication UI components

### For Testing
1. Install test dependencies: `pip install -r tests/requirements.txt`
2. Run property tests: `python -m pytest tests/property/ -v`
3. Test authentication manually: `python backend/test_auth_manual.py`
4. Review test documentation: `tests/README.md`

## 📁 Project Structure

```
SkinGuard/
├── .kiro/specs/derman-ai-skin-screening/
│   ├── requirements.md         # Feature requirements
│   ├── design.md              # System design
│   └── tasks.md               # Implementation tasks
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── auth.py            # Authentication utilities
│   │   ├── dependencies.py    # RBAC middleware
│   │   └── routers/
│   │       └── auth.py        # Auth endpoints
│   ├── requirements.txt       # Backend dependencies
│   ├── .env.example           # Environment template
│   └── README.md              # Backend documentation
├── database/
│   ├── migrations/            # SQL migration files
│   ├── scripts/               # Setup and verification scripts
│   ├── README.md              # Database documentation
│   └── QUICK_REFERENCE.md     # SQL operations guide
├── tests/
│   ├── property/              # Property-based tests
│   ├── README.md              # Test documentation
│   └── requirements.txt       # Test dependencies
├── .env                       # Your credentials (DO NOT COMMIT)
├── GETTING_STARTED.md         # This file
├── GETTING_STARTED_BACKEND.md # Backend quick start
├── TASK_1_COMPLETION_SUMMARY.md  # Task 1 summary
└── TASK_2_COMPLETION_SUMMARY.md  # Task 2 summary
```

## 🔑 Important Files

- **Database Schema**: `database/migrations/001_initial_schema.sql`
- **RLS Policies**: `database/migrations/002_rls_policies.sql`
- **Storage Setup**: `database/migrations/003_storage_setup.sql`
- **Design Document**: `.kiro/specs/derman-ai-skin-screening/design.md`
- **Requirements**: `.kiro/specs/derman-ai-skin-screening/requirements.md`
- **Tasks**: `.kiro/specs/derman-ai-skin-screening/tasks.md`

## 🛠️ Common Commands

### Database
```bash
# Verify database setup
python database/scripts/verify_setup.py

# Connect to database
psql $DATABASE_URL

# Run a specific migration
psql $DATABASE_URL -f database/migrations/001_initial_schema.sql
```

### Testing
```bash
# Run all tests
pytest

# Run property tests only
pytest tests/property/ -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Development
```bash
# Start backend server
cd backend
python -m app.main

# Test authentication
python backend/test_auth_manual.py

# View API docs
# Open http://localhost:8000/api/docs

# Start frontend (once implemented)
cd frontend
npm run dev
```

## 🐛 Troubleshooting

### "No module named pytest"
```bash
pip install -r tests/requirements.txt
```

### "No module named psycopg2"
```bash
pip install -r database/requirements.txt
```

### "Connection refused"
Check your `DATABASE_URL` in `.env` - make sure:
- Password is correct
- Project URL is correct
- Database is running (check Supabase Dashboard)

### "Permission denied"
On Linux/Mac, make scripts executable:
```bash
chmod +x database/scripts/setup.sh
chmod +x tests/run_property_tests.sh
```

### Property tests skip
This is normal if `DATABASE_URL` is not set. Set it up first:
```bash
export DATABASE_URL="postgresql://..."
pytest tests/property/ -v
```

## 📚 Learning Resources

### Supabase
- Docs: https://supabase.com/docs
- Database Guide: https://supabase.com/docs/guides/database
- Storage Guide: https://supabase.com/docs/guides/storage

### PostgreSQL
- Tutorial: https://www.postgresql.org/docs/current/tutorial.html
- SQL Reference: https://www.postgresql.org/docs/current/sql.html

### Property-Based Testing
- Hypothesis: https://hypothesis.readthedocs.io/
- Introduction: https://hypothesis.works/articles/what-is-property-based-testing/

## 🎯 Current Status

✅ **Task 1 Complete**: Database Schema and Infrastructure Setup
- 8 tables created
- 20+ indexes for performance
- 40+ RLS policies for security
- Storage bucket configured
- Property tests implemented

✅ **Task 2 Complete**: Authentication and User Management Backend
- User registration with role assignment
- JWT token authentication
- Login, logout, refresh endpoints
- Role-based access control middleware
- Password hashing and validation
- Comprehensive API documentation

⏭️ **Next Task**: Task 3 - Checkpoint - Authentication System

## 💡 Tips

1. **Keep credentials secure**: Never commit `.env` file
2. **Use RLS**: Always rely on Row Level Security for access control
3. **Test early**: Run property tests after each change
4. **Read the docs**: Check `database/README.md` and `tests/README.md`
5. **Follow the tasks**: Use `.kiro/specs/derman-ai-skin-screening/tasks.md` as your guide

## 🤝 Need Help?

1. Check the documentation in `database/` and `tests/`
2. Review the design document for architecture details
3. Look at the quick reference for common SQL operations
4. Check Supabase Dashboard for database status
5. Review error messages carefully - they usually point to the issue

## 🎉 You're Ready!

The database is set up and ready for development. Start with Task 2 in the tasks.md file to implement the authentication backend.

Good luck building SkinGuard! 🚀

---

*Last updated: February 10, 2024*
