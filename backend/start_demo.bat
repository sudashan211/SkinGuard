@echo off
cd /d "%~dp0"
echo Starting SkinGuard Backend in DEMO MODE...
echo.
echo Demo credentials:
echo   Patient: patient@demo.com / demo123
echo   Doctor: doctor@demo.com / demo123
echo   Admin: admin@demo.com / demo123
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
