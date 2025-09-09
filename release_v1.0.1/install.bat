@echo off
echo Auto Mudfish VPN Installer
echo ==========================

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo This installer requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Installing Auto Mudfish VPN...

REM Create application directory
if not exist "%PROGRAMFILES%\Auto Mudfish" mkdir "%PROGRAMFILES%\Auto Mudfish"

REM Copy executable
echo Copying executable...
copy "AutoMudfish.exe" "%PROGRAMFILES%\Auto Mudfish\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Auto Mudfish.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\Auto Mudfish\AutoMudfish.exe'; $Shortcut.IconLocation = '%PROGRAMFILES%\Auto Mudfish\AutoMudfish.exe,0'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Auto Mudfish" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Auto Mudfish"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Auto Mudfish\Auto Mudfish.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\Auto Mudfish\AutoMudfish.exe'; $Shortcut.IconLocation = '%PROGRAMFILES%\Auto Mudfish\AutoMudfish.exe,0'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo.
echo Auto Mudfish VPN has been installed to:
echo   %PROGRAMFILES%\Auto Mudfish\
echo.
echo Shortcuts have been created on:
echo   - Desktop
echo   - Start Menu
echo.
echo You can now run Auto Mudfish from either shortcut.
echo.
pause
