# ✅ Railway Deployment Checklist

Use this checklist to ensure smooth deployment of SkinGuard to Railway.

---

## 📦 PREPARATION PHASE

### Code Preparation
- [ ] All code is committed locally
- [ ] `.env` files contain NO real credentials (use `.env.example`)
- [ ] `.gitignore` includes `.env`, `node_modules/`, `__pycache__/`
- [ ] Backend runs locally without errors
- [ ] Frontend runs locally without errors
- [ ] Database schema is in `database_setup.sql`

### Required Files Created
- [ ] `backend/Procfile` (created ✓)
- [ ] `backend/runtime.txt` (created ✓)
- [ ] `backend/.env.example` (for reference)
- [ ] `frontend/.env.example` (for reference)

---

## 🔑 ACCOUNTS & CREDENTIALS

### Accounts Setup
- [ ] GitHub account created
- [ ] Railway account created (can use GitHub login)
- [ ] GitHub Student Pack activated (optional, for free credits)

### API Keys Ready
- [ ] Google Maps API key
- [ ] Hugging Face API key
- [ ] SMTP credentials (Gmail app password)
- [ ] JWT secret generated (random 32+ character string)

---

## 🐙 GITHUB SETUP

### Repository Creation
- [ ] GitHub repository created
- [ ] Repository is Private (recommended) or Public
- [ ] Repository name: `SkinGuard` or similar

### Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Railway deployment ready"
git remote add origin https://github.com/YOUR_USERNAME/SkinGuard.git
git branch -M main
git push -u origin main
```

- [ ] Code successfully pushed to GitHub
- [ ] All files visible in GitHub repository

---

## 🚂 RAILWAY PROJECT SETUP

### Create Project
- [ ] Logged into Railway (https://railway.app)
- [ ] New project created
- [ ] GitHub repository connected to Railway

---

## 🗄️ DATABASE SETUP

### PostgreSQL Service
- [ ] PostgreSQL database added to Railway project
- [ ] Database is running (check status indicator)
- [ ] `DATABASE_URL` environment variable available

### Database Schema
- [ ] Database setup SQL script ready
- [ ] Railway CLI installed: `npm i -g @railway/cli`
- [ ] Railway CLI logged in: `railway login`
- [ ] Project linked: `railway link`
- [ ] Database schema executed:
  ```bash
  railway run --service backend psql $DATABASE_URL -f database_setup.sql
  ```
- [ ] Database tables created successfully

---

## 🔧 BACKEND DEPLOYMENT

### Backend Service Setup
- [ ] Backend service added to Railway
- [ ] Root directory set to: `backend`
- [ ] Start command configured: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Service is deploying/running

### Backend Environment Variables
Go to Backend service → Variables tab and add:

- [ ] `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
- [ ] `JWT_SECRET` = (your secret key)
- [ ] `SMTP_SERVER` = smtp.gmail.com
- [ ] `SMTP_PORT` = 587
- [ ] `SMTP_USERNAME` = (your email)
- [ ] `SMTP_PASSWORD` = (your app password)
- [ ] `GOOGLE_MAPS_API_KEY` = (your key)
- [ ] `HUGGINGFACE_API_KEY` = (your key)
- [ ] `ENVIRONMENT` = production

### Backend Verification
- [ ] Backend deployment successful (check status)
- [ ] Health check accessible: `https://<backend-url>/health`
- [ ] Backend URL copied for frontend configuration

---

## 🎨 FRONTEND DEPLOYMENT

### Frontend Service Setup
- [ ] Frontend service added to Railway
- [ ] Root directory set to: `frontend`
- [ ] Build command: `npm install && npm run build`
- [ ] Start command: `npm run preview -- --host 0.0.0.0 --port $PORT`
- [ ] Service is deploying/running

### Frontend Environment Variables
Go to Frontend service → Variables tab and add:

- [ ] `VITE_API_URL` = `https://<your-backend-url>.up.railway.app`

**Note:** Replace `<your-backend-url>` with actual backend URL from Railway!

### Frontend Verification
- [ ] Frontend deployment successful
- [ ] Frontend accessible: `https://<frontend-url>/`
- [ ] No console errors in browser DevTools
- [ ] Frontend can connect to backend

---

## 🔗 CORS CONFIGURATION

### Update Backend CORS
- [ ] Backend `main.py` includes Railway frontend URL in CORS
- [ ] Example:
  ```python
  allow_origins=[
      "http://localhost:3000",
      "https://<your-frontend>.up.railway.app",
      "https://*.railway.app"
  ]
  ```
- [ ] Changes committed and pushed to GitHub
- [ ] Railway auto-deployed new changes

---

## 🧪 TESTING PHASE

### Basic Functionality Tests
- [ ] Homepage loads without errors
- [ ] User registration works
- [ ] User login works
- [ ] Email verification sent (check SMTP)

### Core Feature Tests
- [ ] Image upload works
- [ ] Camera capture works (on mobile/supported browsers)
- [ ] NSFW filter rejects inappropriate images
- [ ] Symptom questionnaire works
- [ ] AI analysis completes successfully
- [ ] Risk level displayed correctly
- [ ] Analysis results saved to database

### Appointment System Tests
- [ ] Hospital search returns results
- [ ] Google Maps displays correctly
- [ ] Appointment booking works
- [ ] Appointment confirmation email sent
- [ ] Hospital staff can review appointments

### Database Tests
- [ ] User data persisted correctly
- [ ] Analysis reports saved
- [ ] Appointments created
- [ ] Audit logs recording events

---

## 🎛️ OPTIONAL ENHANCEMENTS

### Custom Domain (Requires Pro Plan)
- [ ] Custom domain purchased
- [ ] Domain added to Railway service
- [ ] DNS records configured
- [ ] SSL certificate active

### Monitoring & Alerts
- [ ] Railway logs reviewed for errors
- [ ] Error tracking set up (optional)
- [ ] Uptime monitoring configured (optional)

### Performance Optimization
- [ ] Frontend assets optimized
- [ ] Database indexes created
- [ ] Image compression enabled
- [ ] CDN configured (optional)

---

## 📊 POST-DEPLOYMENT

### Documentation
- [ ] Deployment URLs documented
- [ ] Credentials stored securely (password manager)
- [ ] Team members have access (if applicable)

### Backup & Recovery
- [ ] Database backup strategy planned
- [ ] Regular database backups scheduled
- [ ] Disaster recovery plan documented

### Maintenance
- [ ] Monitoring set up for uptime
- [ ] Railway credit usage tracked
- [ ] Regular updates planned

---

## 💰 COST TRACKING

### Railway Usage
- [ ] Current credit balance checked
- [ ] Estimated monthly cost: __________
- [ ] Billing alerts configured (if on Pro plan)

### Expected Costs
- Backend: ~$3-5/month
- Frontend: ~$2-3/month  
- PostgreSQL: ~$5-7/month
- **Total: ~$10-15/month**

**Free Tier:** $5/month credit  
**With GitHub Student Pack:** $10/month credit

---

## 🆘 TROUBLESHOOTING

### Common Issues Checklist
- [ ] Logs reviewed for errors
- [ ] Environment variables double-checked
- [ ] Database connection verified
- [ ] CORS configuration correct
- [ ] Railway service status confirmed

### Support Resources
- [ ] Railway docs bookmarked: https://docs.railway.app
- [ ] Railway Discord joined: https://discord.gg/railway
- [ ] Deployment guide reviewed: `RAILWAY_DEPLOYMENT_GUIDE.md`

---

## ✅ DEPLOYMENT COMPLETE!

### Final Verification
- [ ] All tests passing
- [ ] No critical errors in logs
- [ ] Application accessible to public
- [ ] Performance acceptable
- [ ] Users can complete full workflow

### Share Your Success!
- [ ] Share URL with stakeholders
- [ ] Add URL to thesis/documentation
- [ ] Demonstrate to supervisor/examiner

---

**Deployment Date:** __________________  
**Deployed By:** __________________  
**Frontend URL:** __________________  
**Backend URL:** __________________  
**Status:** 🟢 Live / 🟡 Testing / 🔴 Issues

---

## 📞 Need Help?

If any item is unchecked and causing issues:

1. Review `RAILWAY_DEPLOYMENT_GUIDE.md` (detailed guide)
2. Check `RAILWAY_QUICK_START.md` (quick reference)
3. Review Railway logs (most helpful for debugging)
4. Ask on Railway Discord: https://discord.gg/railway

Good luck with your deployment! 🚀

