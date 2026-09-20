@echo off
title Joyory SmartMatch Launcher
echo ========================================================
echo        Starting Joyory SmartMatch Web Application       
echo ========================================================
echo.

echo [1/2] Starting Django REST Backend on http://localhost:8000 ...
start "Joyory Django Backend" cmd /k "cd /d %~dp0backend && .\venv\Scripts\activate && python manage.py runserver 8000"

echo [2/2] Starting React Frontend on http://localhost:3000 ...
start "Joyory React Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ========================================================
echo  Both servers have been launched in separate windows!
echo  Backend:  http://localhost:8000/
echo  Frontend: http://localhost:3000/
echo ========================================================
pause
