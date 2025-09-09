@echo off
echo Setting up Mudfish credentials...
echo.
.\venv\Scripts\python.exe main.py --setup
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Failed to setup credentials
    echo.
) else (
    echo.
    echo Setup complete! You can now use start_mudfish.bat
    echo.
)
pause
