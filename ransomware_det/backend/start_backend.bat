@echo off
echo ========================================
echo R.A.P.T.O.R Backend Server
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting FastAPI server...
echo Server will run on http://localhost:8000
echo Press Ctrl+C to stop
echo ========================================
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000
