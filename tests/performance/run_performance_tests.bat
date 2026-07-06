@echo off
REM Performance Testing Suite for SkinGuard (Windows)
REM Runs all performance tests and generates a comprehensive report

echo ==========================================
echo SkinGuard Performance Testing Suite
echo ==========================================
echo.

REM Check if backend is running
echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓ Backend is running[0m
) else (
    echo [31m✗ Backend is not running[0m
    echo Please start the backend server: cd backend ^&^& uvicorn app.main:app --reload
    exit /b 1
)

REM Check if frontend is running
echo Checking if frontend is running...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓ Frontend is running[0m
) else (
    echo [33m⚠ Frontend is not running[0m
    echo Some tests may be skipped. Start frontend: cd frontend ^&^& npm run dev
)

echo.
echo ==========================================
echo 1. Backend Performance Tests
echo ==========================================
echo.

cd /d "%~dp0\.."

REM Run AI performance tests
echo Running AI performance tests...
python -m pytest performance/test_ai_performance.py -v -s -m performance

if %errorlevel% equ 0 (
    echo [32m✓ AI performance tests passed[0m
) else (
    echo [31m✗ AI performance tests failed[0m
    exit /b 1
)

echo.
echo ==========================================
echo 2. Load Testing (Optional)
echo ==========================================
echo.

set /p LOAD_TEST="Run load test? This will take 5 minutes (y/N): "
if /i "%LOAD_TEST%"=="y" (
    echo Running load test with 50 users for 5 minutes...
    cd performance
    locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 5m --headless
    
    if %errorlevel% equ 0 (
        echo [32m✓ Load test completed[0m
    ) else (
        echo [31m✗ Load test failed[0m
    )
    cd ..
) else (
    echo Skipping load test
)

echo.
echo ==========================================
echo 3. Frontend Performance Tests
echo ==========================================
echo.

curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    cd ..\frontend
    
    echo Running E2E performance tests...
    call npm run test:performance
    
    if %errorlevel% equ 0 (
        echo [32m✓ Frontend performance tests passed[0m
    ) else (
        echo [31m✗ Frontend performance tests failed[0m
    )
    
    cd ..\tests
) else (
    echo [33m⚠ Skipping frontend tests (frontend not running)[0m
)

echo.
echo ==========================================
echo 4. Bundle Analysis
echo ==========================================
echo.

cd ..\frontend

echo Building and analyzing bundle...
call npm run build

REM Check bundle size
for %%F in (dist\assets\*.js) do (
    echo Bundle: %%~nxF - %%~zF bytes
)

cd ..\tests

echo.
echo ==========================================
echo Performance Testing Complete
echo ==========================================
echo.
echo Summary:
echo   - AI Performance: Check test output above
echo   - Load Testing: Check Locust report
echo   - Frontend Performance: Check Playwright report
echo   - Bundle Size: Check output above
echo.
echo Next steps:
echo   1. Review test results
echo   2. Check performance metrics
echo   3. Run Lighthouse audit: cd frontend ^&^& npm run lighthouse
echo   4. Monitor production metrics
echo.

pause
