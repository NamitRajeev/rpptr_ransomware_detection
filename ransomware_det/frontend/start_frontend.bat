@echo off
echo ========================================
echo R.A.P.T.O.R Frontend Dashboard
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Node.js installation...
node --version
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Vite development server...
echo Dashboard will open at http://localhost:5173
echo Press Ctrl+C to stop
echo ========================================
echo.

call npm run dev
