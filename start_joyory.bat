@echo off
setlocal enabledelayedexpansion
title Joyory SmartMatch — Launcher

REM ══════════════════════════════════════════════════════════════
REM  Joyory SmartMatch — One-Command Local Startup
REM  Usage: .\start_joyory.bat   (from project root)
REM
REM  What this does:
REM    1. Validates Python venv and Django installation
REM    2. Validates Node/npm and React dependencies
REM    3. Launches Django backend in a separate window (port 8000)
REM    4. Launches React frontend in a separate window (port 3000)
REM
REM  What this does NOT do:
REM    - Does NOT delete or reset your SQLite database
REM    - Does NOT run model training or data import scripts
REM    - Does NOT install packages automatically (run setup first)
REM ══════════════════════════════════════════════════════════════

echo.
echo  ========================================================
echo     J O Y O R Y   S M A R T M A T C H
echo     Smart Beauty Shopping Experience
echo  ========================================================
echo.

REM ── Step 1: Locate the project root (the folder this .bat is in)
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "VENV=%BACKEND%\venv"
set "PYTHON=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"
set "ACTIVATE=%VENV%\Scripts\activate.bat"

echo  [Check] Project root: %ROOT%
echo.

REM ── Step 2: Validate Python virtual environment
echo  [1/5] Checking Python virtual environment...
if not exist "%PYTHON%" (
    echo.
    echo  ERROR: Python virtual environment not found.
    echo  Expected location: %PYTHON%
    echo.
    echo  To fix this, run from the 'backend' folder:
    echo      python -m venv venv
    echo      venv\Scripts\activate
    echo      pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo         Found: %PYTHON%

REM ── Step 3: Validate Django is installed
echo  [2/5] Checking Django installation...
"%PYTHON%" -c "import django; print('         Django', django.__version__, 'OK')" 2>nul
if errorlevel 1 (
    echo.
    echo  ERROR: Django is not installed in the virtual environment.
    echo  Run: cd backend ^& venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM ── Step 4: Check the database exists
echo  [3/5] Checking SQLite database...
if not exist "%BACKEND%\db.sqlite3" (
    echo         Database not found. Running migrations...
    cd /d "%BACKEND%"
    "%PYTHON%" manage.py migrate --run-syncdb
    cd /d "%ROOT%"
) else (
    echo         Found: %BACKEND%\db.sqlite3
)

REM ── Step 5: Validate Node / npm
echo  [4/5] Checking Node.js and npm...
where npm >nul 2>nul
if errorlevel 1 (
    echo.
    echo  ERROR: npm not found. Install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('npm --version 2^>nul') do set NPM_VER=%%v
echo         npm %NPM_VER% found.

REM ── Step 6: Check node_modules
echo  [5/5] Checking React dependencies...
if not exist "%FRONTEND%\node_modules" (
    echo         node_modules not found. Running npm install...
    cd /d "%FRONTEND%"
    npm install
    cd /d "%ROOT%"
) else (
    echo         node_modules: OK
)

echo.
echo  ========================================================
echo   All checks passed. Launching servers...
echo  ========================================================
echo.

REM ── Launch Django backend
echo  [Starting] Django backend on http://localhost:8000 ...
start "Joyory — Django Backend (port 8000)" cmd /k "title Joyory Backend ^& cd /d %BACKEND% ^& call %ACTIVATE% ^& echo. ^& echo  Backend ready: http://localhost:8000/api/ ^& echo  Press Ctrl+C to stop. ^& echo. ^& python manage.py runserver 8000"

REM ── Small pause to let backend initialise before frontend
timeout /t 3 /nobreak >nul

REM ── Launch React frontend
echo  [Starting] React frontend on http://localhost:3000 ...
start "Joyory — React Frontend (port 3000)" cmd /k "title Joyory Frontend ^& cd /d %FRONTEND% ^& echo. ^& echo  Frontend starting: http://localhost:3000 ^& echo  Press Ctrl+C to stop. ^& echo. ^& npm start"

echo.
echo  ========================================================
echo   Joyory SmartMatch is launching!
echo.
echo   Backend API:   http://localhost:8000/api/
echo   Frontend App:  http://localhost:3000/
echo   Dashboard:     http://localhost:3000/dashboard
echo   Admin panel:   http://localhost:8000/admin/
echo.
echo   Two separate windows have opened.
echo   Close them (or press Ctrl+C inside) to stop the servers.
echo  ========================================================
echo.
echo   URLs to bookmark:
echo     /          - Homepage
echo     /quiz      - SmartMatch Quiz
echo     /dashboard - Unified Dashboard
echo     /routine   - Routine Builder
echo     /ingredient-check - Ingredient Safety Checker
echo     /reviews   - Review Insights
echo     /compare   - Product Comparison
echo.
pause
endlocal
