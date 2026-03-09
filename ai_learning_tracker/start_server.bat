@echo off
echo ========================================
echo  AI Learning Tracker Portal
echo ========================================
echo.
echo Starting server...
echo.
cd /d "%~dp0"
call ..\LC\Scripts\activate.bat
python manage.py runserver
