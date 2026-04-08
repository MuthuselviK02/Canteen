@echo off
echo === Image URL Management System ===
echo.

cd /d "%~dp0"

echo Choose an option:
echo 1. Get current image URLs (for manual copy-paste)
echo 2. Update all menu items with current URLs
echo 3. Show current configuration
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto get_urls
if "%choice%"=="2" goto update_urls
if "%choice%"=="3" goto show_config
if "%choice%"=="4" goto end
goto invalid

:get_urls
echo.
echo === Getting Current Image URLs ===
python flexible_image_urls.py
goto end

:update_urls
echo.
echo === Updating All Menu Items ===
python update_all_image_urls.py
goto end

:show_config
echo.
echo === Current Configuration ===
if exist image_config.py (
    type image_config.py
) else (
    echo Configuration file not found!
)
goto end

:invalid
echo.
echo Invalid choice! Please try again.
goto end

:end
echo.
echo Done!
pause
