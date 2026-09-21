# ========================================================
#   J O Y O R Y   S M A R T M A T C H
#   PowerShell Native Startup Script
#   Usage: .\start_joyory.ps1
# ========================================================

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Python = Join-Path $Backend "venv\Scripts\python.exe"

Write-Host ""
Write-Host " ========================================================" -ForegroundColor DarkMagenta
Write-Host "    J O Y O R Y   S M A R T M A T C H" -ForegroundColor Magenta
Write-Host "    Smart Beauty Shopping Experience" -ForegroundColor Magenta
Write-Host " ========================================================" -ForegroundColor DarkMagenta
Write-Host ""

# [1/5] Check Python venv
Write-Host " [1/5] Checking Python virtual environment..." -NoNewline
if (-not (Test-Path $Python)) {
    Write-Host "`n ERROR: Python virtual environment not found at: $Python" -ForegroundColor Red
    exit 1
}
Write-Host " OK ($Python)" -ForegroundColor Green

# [2/5] Check Django
Write-Host " [2/5] Checking Django installation..." -NoNewline
try {
    $djangoVer = & $Python -c "import django; print(django.__version__)"
    Write-Host " OK (Django $djangoVer)" -ForegroundColor Green
} catch {
    Write-Host "`n ERROR: Django is not installed in the virtual environment." -ForegroundColor Red
    exit 1
}

# [3/5] Check Database
Write-Host " [3/5] Checking SQLite database..." -NoNewline
$dbPath = Join-Path $Backend "db.sqlite3"
if (Test-Path $dbPath) {
    Write-Host " OK ($dbPath)" -ForegroundColor Green
} else {
    Write-Host " Not found, running migrations..." -ForegroundColor Yellow
    Push-Location $Backend
    & $Python manage.py migrate --run-syncdb
    Pop-Location
}

# [4/5] Check Node / npm
Write-Host " [4/5] Checking Node.js and npm..." -NoNewline
try {
    $npmVer = npm --version
    Write-Host " OK (npm $npmVer)" -ForegroundColor Green
} catch {
    Write-Host "`n ERROR: npm not found. Please install Node.js." -ForegroundColor Red
    exit 1
}

# [5/5] Check React dependencies
Write-Host " [5/5] Checking React dependencies..." -NoNewline
$nodeModules = Join-Path $Frontend "node_modules"
if (Test-Path $nodeModules) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " Installing dependencies..." -ForegroundColor Yellow
    Push-Location $Frontend
    npm install
    Pop-Location
}

Write-Host ""
Write-Host " ========================================================" -ForegroundColor DarkMagenta
Write-Host "  All checks passed. Launching servers..." -ForegroundColor Green
Write-Host " ========================================================" -ForegroundColor DarkMagenta
Write-Host ""

# Start Django Backend in a separate window
Write-Host " [Starting] Django backend on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process cmd.exe -ArgumentList "/k title Joyory Backend && cd /d `"$Backend`" && `"$Python`" manage.py runserver 8000"

# Pause briefly
Start-Sleep -Seconds 2

# Start React Frontend in a separate window
Write-Host " [Starting] React frontend on http://localhost:3000 ..." -ForegroundColor Cyan
Start-Process cmd.exe -ArgumentList "/k title Joyory Frontend && cd /d `"$Frontend`" && npm start"

# Wait a few seconds for servers to initialize, then open browser
Start-Sleep -Seconds 4
Write-Host " [Launching] Opening browser at http://localhost:3000 ..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host " ========================================================" -ForegroundColor DarkMagenta
Write-Host "  Joyory SmartMatch is running!" -ForegroundColor Green
Write-Host "  Backend API:   http://localhost:8000/api/" -ForegroundColor White
Write-Host "  Frontend App:  http://localhost:3000/" -ForegroundColor White
Write-Host "  Dashboard:     http://localhost:3000/dashboard" -ForegroundColor White
Write-Host " ========================================================" -ForegroundColor DarkMagenta
Write-Host ""
