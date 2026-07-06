@echo off
echo ========================================
echo Fixing Dependency Conflicts
echo ========================================
echo.

echo Step 1: Upgrading ml_dtypes...
python -m pip install --upgrade ml_dtypes
echo.

echo Step 2: Upgrading jax...
python -m pip install --upgrade jax
echo.

echo Step 3: Testing...
python test_huggingface_model.py ../ISIC_0000198.jpg
echo.

echo ========================================
echo Done!
echo ========================================
pause
