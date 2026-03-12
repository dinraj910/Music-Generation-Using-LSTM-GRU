@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM Neural Music Generation - Quick Start Script (Windows)
REM ═══════════════════════════════════════════════════════════════════════

echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║          🎵 Neural Music Generation Web App 🎵                ║
echo  ║              LSTM · GRU · BiLSTM Models                       ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Check if venv exists
if exist "venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] No virtual environment found. Using system Python.
    echo [!] Run: python -m venv venv
)

REM Check dependencies
echo [*] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [*] Starting Flask server...
echo [*] Open your browser to: http://localhost:5000
echo [*] Press Ctrl+C to stop the server
echo.

python app.py

pause
