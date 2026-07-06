# SkinGuard Backend Deployment Guide

**Version**: 1.0  
**Last Updated**: February 12, 2026  
**Backend Progress**: 92% Complete

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [AI Models Setup](#ai-models-setup)
6. [Storage Configuration](#storage-configuration)
7. [Email and Notifications](#email-and-notifications)
8. [Video Consultation Setup](#video-consultation-setup)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Security Checklist](#security-checklist)
11. [Testing Deployment](#testing-deployment)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.10 or higher
- PostgreSQL 14+ with PostGIS extension
- Git
- pip or uv (Python package manager)

### Required Accounts
- Supabase account (for database and storage)
- SendGrid or AWS SES account (for email notifications)
- Twilio or Agora account (for video consultations)
- Google Maps API key (for doctor locator)

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB minimum (for AI models and images)
- **Network**: Stable internet connection

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd skinguard-backend
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
DATABASE_URL=postgresql://user:password@host:port/database

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@skinguard.com

# Video Consultation
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_API_KEY=your-twilio-api-key
TWILIO_API_SECRET=your-twilio-api-secret

# Google Maps
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# AI Models
MODEL_CACHE_DIR=./models
NSFW_MODEL_PATH=./models/nsfw_detector
SWIN_MODEL_PATH=./models/swin_transformer
EFFICIENTNET_MODEL_PATH=./models/efficientnet_b7

# Storage
STORAGE_BUCKET=medical-images
MAX_UPLOAD_SIZE_MB=10

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

**Security Note**: Never commit `.env` files to version control!

---

## Database Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and API keys
4. Enable PostGIS extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS cube;
   CREATE EXTENSION IF NOT EXISTS earthdistance;
   ```

### 2. Run Database Migrations

```bash
# Navigate to database directory
cd database/migrations

# Run migrations in order
psql $DATABASE_URL -f 001_initial_schema.sql
psql $DATABASE_URL -f 002_indexes_and_rls.sql
psql $DATABASE_URL -f 003_audit_logs.sql
psql $DATABASE_URL -f 004_skin_wiki_tables.sql
```

### 3. Verify Database Setup

```bash
# Run verification script
python tests/verify_database_setup.py
```

Expected output:
```
✓ All 10 tables created
✓ All indexes created
✓ RLS policies enabled
✓ PostGIS extension active
```

### 4. Configure Row Level Security (RLS)

RLS policies are automatically created by migration scripts. Verify they're active:

```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

All tables should have `rowsecurity = true`.

---

## Backend Deployment

### Option 1: Local Development Server

```bash
# Start FastAPI server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access API documentation at: `http://localhost:8000/docs`

### Option 2: Production with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Start with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Option 3: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY database/ ./database/

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "backend.app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

Build and run:

```bash
# Build image
docker build -t skinguard-backend .

# Run container
docker run -d \
  --name skinguard-api \
  -p 8000:8000 \
  --env-file .env \
  skinguard-backend
```

### Option 4: AWS Lambda Deployment

Use Mangum adapter for serverless deployment:

```python
# backend/app/main.py
from mangum import Mangum

app = FastAPI()
# ... your routes ...

# Lambda handler
handler = Mangum(app)
```

Deploy with AWS SAM or Serverless Framework.

### Option 5: Cloud Platform Deployment

#### Heroku
```bash
# Create Procfile
echo "web: gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:\$PORT" > Procfile

# Deploy
heroku create skinguard-api
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### Render
1. Connect GitHub repository
2. Select "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn backend.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

---

## AI Models Setup

### 1. Download Pre-trained Models

```bash
# Create models directory
mkdir -p models

# Download NSFW detector
python scripts/download_nsfw_model.py

# Download Swin Transformer
python scripts/download_swin_model.py

# Download EfficientNet-B7
python scripts/download_efficientnet_model.py
```

### 2. Verify Model Loading

```bash
# Test model loading
python tests/test_model_loading.py
```

Expected output:
```
✓ NSFW detector loaded (size: 150MB)
✓ Swin Transformer loaded (size: 350MB)
✓ EfficientNet-B7 loaded (size: 260MB)
✓ All models ready
```

### 3. GPU Configuration (Optional)

For faster inference, use GPU:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 4. Model Optimization

For production, optimize models:

```python
# Convert to TorchScript for faster inference
import torch

model = load_model()
scripted_model = torch.jit.script(model)
scripted_model.save("model_optimized.pt")
```

---

## Storage Configuration

### 1. Supabase Storage Setup

```bash
# Create storage bucket
curl -X POST 'https://your-project.supabase.co/storage/v1/bucket' \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "medical-images",
    "name": "medical-images",
    "public": false
  }'
```

### 2. Configure Storage Policies

```sql
-- Allow authenticated users to upload
CREATE POLICY "Users can upload their own images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'medical-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow users to read their own images
CREATE POLICY "Users can read their own images"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'medical-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

### 3. Configure Image Encryption

Enable AES-256 encryption in Supabase dashboard:
1. Go to Storage settings
2. Enable "Encrypt files at rest"
3. Save changes

### 4. Set Upload Limits

```python
# backend/app/config.py
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MIN_IMAGE_SIZE = (512, 512)
```

---

## Email and Notifications

### 1. SendGrid Setup

```bash
# Install SendGrid
pip install sendgrid

# Verify API key
python -c "from sendgrid import SendGridAPIClient; sg = SendGridAPIClient('$SENDGRID_API_KEY'); print('✓ SendGrid connected')"
```

### 2. Email Templates

Create email templates in `backend/app/email_templates/`:

- `analysis_complete.html` - Analysis results notification
- `appointment_confirmation.html` - Appointment booking
- `appointment_reminder.html` - 24h reminder
- `doctor_verification.html` - Verification status
- `follow_up_reminder.html` - 6-month follow-up
- `urgent_case_alert.html` - Emergency notification

### 3. Test Email Delivery

```bash
# Send test email
python tests/test_email_delivery.py --to your-email@example.com
```

### 4. Configure Email Sending

```python
# backend/app/notification_service.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email, subject, html_content):
    message = Mail(
        from_email='noreply@skinguard.com',
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    response = sg.send(message)
    return response.status_code == 202
```

---

## Video Consultation Setup

### 1. Twilio Setup

```bash
# Install Twilio
pip install twilio

# Create Twilio account and get credentials
# Add to .env file
```

### 2. Create Video Rooms

```python
# backend/app/video_service.py
from twilio.rest import Client

def create_video_room(appointment_id):
    client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_API_KEY')
    )
    
    room = client.video.rooms.create(
        unique_name=f"appointment-{appointment_id}",
        type='group',
        max_participants=2
    )
    
    return room.url
```

### 3. Generate Access Tokens

```python
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

def generate_token(user_id, room_name):
    token = AccessToken(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_API_KEY'),
        os.getenv('TWILIO_API_SECRET'),
        identity=user_id
    )
    
    grant = VideoGrant(room=room_name)
    token.add_grant(grant)
    
    return token.to_jwt()
```

### 4. Test Video Functionality

```bash
# Test video room creation
python tests/test_video_consultation.py
```

---

## Monitoring and Logging

### 1. Application Logging

Configure logging in `backend/app/main.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 2. Error Tracking with Sentry

```bash
# Install Sentry
pip install sentry-sdk[fastapi]

# Configure Sentry
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

### 3. Performance Monitoring

```python
# Add middleware for request timing
from time import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response
```

### 4. Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

---

## Security Checklist

### Pre-Deployment Security

- [ ] All environment variables in `.env` (not hardcoded)
- [ ] `.env` file in `.gitignore`
- [ ] JWT secret key is strong (32+ characters)
- [ ] Database passwords are strong
- [ ] RLS policies enabled on all tables
- [ ] HTTPS/TLS enabled for all connections
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using parameterized queries)
- [ ] XSS prevention (sanitizing inputs)
- [ ] CSRF protection enabled
- [ ] File upload validation (size, type, content)
- [ ] NSFW filter active
- [ ] Audit logging enabled
- [ ] Error messages don't leak sensitive info

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/analyze-skin")
@limiter.limit("10/minute")
async def analyze_skin(request: Request):
    # ... endpoint logic
    pass
```

---

## Testing Deployment

### 1. Run All Tests

```bash
# Run unit tests
pytest tests/unit/

# Run property-based tests
pytest tests/property/ --hypothesis-show-statistics

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=backend --cov-report=html
```

### 2. Verify API Endpoints

```bash
# Test authentication
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"patient"}'

# Test image analysis
curl -X POST http://localhost:8000/api/analyze-skin \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@test_image.jpg"

# Test doctor search
curl "http://localhost:8000/api/doctors/nearby?lat=40.7128&lng=-74.0060&radius=10"
```

### 3. Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

### 4. Security Scan

```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check

# Run bandit for security issues
pip install bandit
bandit -r backend/
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error**: `could not connect to server`

**Solution**:
```bash
# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Verify Supabase project is active
```

#### 2. AI Models Not Loading

**Error**: `FileNotFoundError: Model not found`

**Solution**:
```bash
# Check model paths
ls -la models/

# Re-download models
python scripts/download_models.py

# Verify MODEL_CACHE_DIR in .env
```

#### 3. Image Upload Fails

**Error**: `413 Request Entity Too Large`

**Solution**:
```python
# Increase max upload size
# In backend/app/main.py
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_request_size=10 * 1024 * 1024  # 10MB
)
```

#### 4. NSFW Filter Too Strict

**Error**: Legitimate images being rejected

**Solution**:
```python
# Adjust thresholds in backend/app/nsfw_filter.py
NSFW_THRESHOLD = 0.45  # Increase from 0.35
NON_SKIN_THRESHOLD = 0.85  # Increase from 0.8
```

#### 5. JWT Token Expired

**Error**: `401 Unauthorized`

**Solution**:
```bash
# Refresh token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"your-refresh-token"}'
```

#### 6. Email Not Sending

**Error**: `SendGrid API error`

**Solution**:
```bash
# Verify API key
curl -X GET https://api.sendgrid.com/v3/user/profile \
  -H "Authorization: Bearer $SENDGRID_API_KEY"

# Check email templates exist
ls backend/app/email_templates/

# Test with a simple email
python tests/test_email_simple.py
```

### Debug Mode

Enable debug mode for detailed error messages:

```python
# backend/app/main.py
app = FastAPI(debug=True)  # Only for development!
```

**Warning**: Never enable debug mode in production!

### Logs Location

```bash
# Application logs
tail -f logs/app.log

# Error logs
tail -f logs/error.log

# Access logs
tail -f logs/access.log
```

---

## Production Checklist

### Before Going Live

- [ ] All tests passing (unit, property, integration)
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] AI models downloaded and tested
- [ ] Storage bucket created and configured
- [ ] Email service configured and tested
- [ ] Video consultation service tested
- [ ] HTTPS/SSL certificate installed
- [ ] CORS configured for production domain
- [ ] Rate limiting enabled
- [ ] Monitoring and logging configured
- [ ] Error tracking (Sentry) configured
- [ ] Backup strategy in place
- [ ] Security audit completed
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] API documentation accessible
- [ ] Health check endpoint working
- [ ] Rollback plan prepared

### Post-Deployment

- [ ] Monitor error rates
- [ ] Check API response times
- [ ] Verify email delivery
- [ ] Test critical user flows
- [ ] Monitor database performance
- [ ] Check storage usage
- [ ] Review security logs
- [ ] Set up alerts for critical errors
- [ ] Document any issues encountered
- [ ] Plan for scaling if needed

---

## Support and Resources

### Documentation
- API Documentation: `http://your-domain/docs`
- Database Schema: `database/schema.md`
- Getting Started: `GETTING_STARTED.md`

### Contact
- Technical Support: support@skinguard.com
- Security Issues: security@skinguard.com

### Useful Commands

```bash
# Start development server
uvicorn backend.app.main:app --reload

# Run tests
pytest

# Check code quality
flake8 backend/
black backend/

# Database migrations
psql $DATABASE_URL -f database/migrations/xxx.sql

# View logs
tail -f logs/app.log

# Check system health
curl http://localhost:8000/health
```

---

**Deployment Guide Version**: 1.0  
**Last Updated**: February 12, 2026  
**Status**: Ready for Production Deployment
