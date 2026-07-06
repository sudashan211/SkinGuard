@echo off
REM SkinGuard Property Test Runner (Windows)
REM Runs property-based tests for database referential integrity

echo ==========================================
echo SkinGuard Property Tests
echo ==========================================
echo.

REM Check if dependencies are installed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo Installing test dependencies...
    pip install -r tests\requirements.txt
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found
    echo Property tests require DATABASE_URL to be set
    echo Tests will be skipped without database connection
    echo.
)

REM Run property tests
echo Running property-based tests...
echo.

python -m pytest tests\property\test_database_properties.py -v --tb=short --hypothesis-show-statistics

echo.
echo ==========================================
echo Property tests complete
echo ==========================================

pause
