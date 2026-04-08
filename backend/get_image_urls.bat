@echo off
echo === Available Image URLs for Menu Management ===
echo.

cd /d "%~dp0"

if not exist "static\images" (
    echo ❌ Images directory not found!
    echo Please run the download_food_images.py script first.
    pause
    exit /b 1
)

echo 📁 Copy these URLs for Menu Management:
echo ====================================================

setlocal enabledelayedexpansion
set count=0

for %%f in (static\images\*.jpg static\images\*.jpeg static\images\*.png static\images\*.gif static\images\*.webp) do (
    set /a count+=1
    echo !count!. http://localhost:8000/static/images/%%~nxf
)

echo ====================================================
echo 📊 Total images available: !count!
echo 🌐 Base URL: http://localhost:8000/static/images/
echo 📂 Local folder: %cd%\static\images
echo.
echo 📝 Instructions:
echo 1. Copy any URL from above
echo 2. Go to Admin Dashboard → Menu Management
echo 3. Edit a menu item
echo 4. Paste the URL in the 'Image URL' field
echo 5. Save the item
echo.
echo 🔄 For new images:
echo 1. Place new image files in: static\images\
echo 2. Run this batch file again to see new URLs
echo 3. Copy the new URL and use in menu management
echo.
pause
