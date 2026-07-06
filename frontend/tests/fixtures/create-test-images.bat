@echo off
REM Script to create placeholder test images for E2E tests
REM Requires ImageMagick to be installed

echo Creating test image fixtures...

REM Check if ImageMagick is installed
where convert >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: ImageMagick is not installed.
    echo Please download and install from: https://imagemagick.org/script/download.php
    exit /b 1
)

REM Create test-lesion.jpg (valid skin lesion image)
echo Creating test-lesion.jpg...
convert -size 512x512 xc:white ^
    -fill "#8B4513" -draw "circle 256,256 256,200" ^
    -fill "#654321" -draw "circle 256,256 256,220" ^
    -fill "#A0522D" -draw "ellipse 256,256 80,60 0,360" ^
    -blur 0x2 ^
    test-lesion.jpg

REM Create low-res-image.jpg (low resolution image)
echo Creating low-res-image.jpg...
convert -size 256x256 xc:white ^
    -fill "#8B4513" -draw "circle 128,128 128,100" ^
    low-res-image.jpg

REM Create melanoma-info.jpg (educational content)
echo Creating melanoma-info.jpg...
convert -size 800x600 xc:white ^
    -pointsize 40 -fill black ^
    -draw "text 200,100 'Melanoma Information'" ^
    -pointsize 20 ^
    -draw "text 100,200 'Most serious type of skin cancer'" ^
    -draw "text 100,250 'Early detection is crucial'" ^
    -draw "text 100,300 'ABCDE warning signs:'" ^
    -draw "text 120,340 'A - Asymmetry'" ^
    -draw "text 120,370 'B - Border irregularity'" ^
    -draw "text 120,400 'C - Color variation'" ^
    -draw "text 120,430 'D - Diameter > 6mm'" ^
    -draw "text 120,460 'E - Evolving'" ^
    melanoma-info.jpg

echo.
echo Test fixtures created successfully!
echo.
echo Created files:
echo   - test-lesion.jpg (512x512, valid skin lesion)
echo   - low-res-image.jpg (256x256, low resolution)
echo   - melanoma-info.jpg (800x600, educational content)
echo.
echo Note: For NSFW testing, please read nsfw-test-note.txt
echo.

pause
