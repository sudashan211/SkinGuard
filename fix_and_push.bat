@echo off
echo ========================================
echo Fixing Git Lock and Pushing to GitHub
echo ========================================

echo.
echo Step 1: Killing any Git processes...
taskkill /F /IM git.exe 2>nul
timeout /t 2 >nul

echo.
echo Step 2: Removing lock file...
if exist .git\index.lock (
    del /f /q .git\index.lock
    echo Lock file removed!
) else (
    echo No lock file found.
)

echo.
echo Step 3: Adding all files...
git add .

echo.
echo Step 4: Committing changes...
git commit -m "Initial commit - SkinGuard AI System"

echo.
echo Step 5: Setting main branch...
git branch -M main

echo.
echo Step 6: Adding remote repository...
git remote add origin https://github.com/sudashan211/SkinGuard.git 2>nul
if errorlevel 1 (
    echo Remote already exists, continuing...
    git remote set-url origin https://github.com/sudashan211/SkinGuard.git
)

echo.
echo Step 7: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done! Check the messages above.
echo ========================================
echo.
pause
