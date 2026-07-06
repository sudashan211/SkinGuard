# SkinGuard Port Configuration

This document outlines all the ports used by the SkinGuard application and its dependencies.

## Application Ports

### Frontend (React/Vite)
- **Port**: `3000`
- **URL**: http://localhost:3000
- **Description**: Main web application interface
- **Service**: Vite development server
- **Configuration**: Default Vite port

### Backend API (FastAPI)
- **Port**: `8001`
- **URL**: http://localhost:8001
- **Description**: REST API server with AI processing
- **Service**: Uvicorn ASGI server
- **Configuration**: Set in `backend/.env` as `API_PORT=8001`
- **API Documentation**: http://localhost:8001/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8001/redoc (ReDoc)

## Database Ports

### PostgreSQL Database
- **Port**: `5432` (default)
- **Host**: localhost
- **Database**: `skinguard`
- **Username**: `postgres`
- **Password**: `12345`
- **Connection String**: `postgresql://postgres:12345@localhost:5432/skinguard`
- **Management Tool**: pgAdmin 4

## Port Usage Summary

| Service | Port | Protocol | Access | Purpose |
|---------|------|----------|--------|---------|
| Frontend | 3000 | HTTP | Public | Web application UI |
| Backend API | 8001 | HTTP | Public | REST API endpoints |
| PostgreSQL | 5432 | TCP | Internal | Database server |

## Network Configuration

### CORS Settings
The backend is configured to accept requests from:
- `http://localhost:3000` (Frontend)
- `http://localhost:5173` (Alternative Vite port)

### API Base URL
Frontend connects to backend via:
- Environment variable: `VITE_API_URL=http://localhost:8001`
- Configuration file: `frontend/.env`

## Port Conflicts

### Common Issues
- **Port 8000**: Originally used for backend, changed to 8001 due to conflicts
- **Port 3000**: Standard React development port
- **Port 5432**: Standard PostgreSQL port

### Alternative Ports
If you need to change ports due to conflicts:

1. **Frontend Port**: Modify Vite configuration or use `--port` flag
2. **Backend Port**: Update `API_PORT` in `backend/.env`
3. **Database Port**: Modify PostgreSQL configuration and update connection string

## Firewall Configuration

### Required Inbound Rules
- Port 3000: Allow HTTP traffic for frontend
- Port 8001: Allow HTTP traffic for API
- Port 5432: Allow local connections for database (localhost only)

### Security Notes
- Database port (5432) should only accept local connections
- API port (8001) serves the application backend
- Frontend port (3000) serves the user interface

## Development vs Production

### Development (Current Setup)
- Frontend: http://localhost:3000
- Backend: http://localhost:8001
- Database: localhost:5432

### Production Considerations
- Use reverse proxy (nginx) on port 80/443
- Database should be on private network
- API should be behind load balancer
- Enable HTTPS with SSL certificates

## Troubleshooting

### Port Already in Use
```bash
# Check what's using a port (Windows)
netstat -ano | findstr :8001

# Kill process using port
taskkill /PID <process_id> /F
```

### Connection Issues
1. Verify services are running on correct ports
2. Check firewall settings
3. Confirm environment variables are set correctly
4. Test connectivity with curl or browser

## Service Status Check

### How to Start Servers

#### Backend Server (Port 8001)
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Frontend Server (Port 3000)
```bash
cd frontend
npm run dev
```

### Frontend
- URL: http://localhost:3000
- Status: Should show SkinGuard login page

### Backend API
- URL: http://localhost:8001/docs
- Status: Should show Swagger API documentation

### Database
- Connection: Use pgAdmin 4 or psql client
- Test query: `SELECT version();`

---

**Last Updated**: March 2026  
**Configuration Version**: PostgreSQL Setup