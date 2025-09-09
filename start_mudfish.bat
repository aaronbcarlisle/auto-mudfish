@echo off
echo Starting Mudfish VPN with stored credentials...
.\venv\Scripts\python.exe main.py --use-stored > output.log 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Failed to start Mudfish VPN
    echo Check output.log for details
    echo.
    echo If this is your first time, run: python main.py --setup
    echo.
)
pause
