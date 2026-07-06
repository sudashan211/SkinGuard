@echo off
echo ========================================
echo Pushing SkinGuard to GitHub
echo ========================================

echo.
echo Step 1: Adding all files...
git add .

echo.
echo Step 2: Committing changes...
git commit -m "Initial commit - SkinGuard AI-Powered Skin Cancer Detection System"

echo.
echo Step 3: Setting main branch...
git branch -M main

echo.
echo Step 4: Adding remote repository...
git remote add origin https://github.com/sudashan211/SkinGuard.git

echo.
echo Step 5: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done! Your code is now on GitHub!
echo ========================================
pause
