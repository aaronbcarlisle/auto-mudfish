@echo off
echo Auto Mudfish VPN - Simple Installer
echo ====================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

echo.
echo Installing Auto Mudfish VPN...
echo.

REM Set installation directory
set "INSTALL_DIR=%PROGRAMFILES%\Auto Mudfish"
echo Installation directory: %INSTALL_DIR%

REM Create installation directory
echo Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy application files
echo Copying application files...
xcopy /E /I /Y "%~dp0..\*" "%INSTALL_DIR%\" /EXCLUDE:exclude.txt

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Auto Mudfish VPN.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '%INSTALL_DIR%\gui.py'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Auto Mudfish VPN'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Auto Mudfish" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Auto Mudfish"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Auto Mudfish\Auto Mudfish VPN.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '%INSTALL_DIR%\gui.py'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Auto Mudfish VPN'; $Shortcut.Save()"

REM Create uninstaller
echo Creating uninstaller...
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo echo Auto Mudfish VPN Uninstaller >> "%INSTALL_DIR%\uninstall.bat"
echo echo ============================= >> "%INSTALL_DIR%\uninstall.bat"
echo echo. >> "%INSTALL_DIR%\uninstall.bat"
echo echo Removing Auto Mudfish VPN... >> "%INSTALL_DIR%\uninstall.bat"
echo echo. >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%%USERPROFILE%%\Desktop\Auto Mudfish VPN.lnk" del "%%USERPROFILE%%\Desktop\Auto Mudfish VPN.lnk" >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%%USERPROFILE%%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Auto Mudfish\Auto Mudfish VPN.lnk" del "%%USERPROFILE%%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Auto Mudfish\Auto Mudfish VPN.lnk" >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%%USERPROFILE%%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Auto Mudfish" rmdir "%%USERPROFILE%%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Auto Mudfish" >> "%INSTALL_DIR%\uninstall.bat"
echo if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%" >> "%INSTALL_DIR%\uninstall.bat"
echo echo. >> "%INSTALL_DIR%\uninstall.bat"
echo echo Uninstallation completed! >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"

REM Create install info
echo Creating installation info...
echo { > "%INSTALL_DIR%\install_info.json"
echo   "version": "1.0.0", >> "%INSTALL_DIR%\install_info.json"
echo   "install_path": "%INSTALL_DIR%", >> "%INSTALL_DIR%\install_info.json"
echo   "install_date": "%DATE% %TIME%", >> "%INSTALL_DIR%\install_info.json"
echo   "desktop_shortcut": true, >> "%INSTALL_DIR%\install_info.json"
echo   "start_menu": true >> "%INSTALL_DIR%\install_info.json"
echo } >> "%INSTALL_DIR%\install_info.json"

echo.
echo Installation completed successfully!
echo.
echo Auto Mudfish VPN has been installed to: %INSTALL_DIR%
echo Desktop shortcut created.
echo Start menu entry created.
echo.
echo You can now launch Auto Mudfish VPN from:
echo - Desktop shortcut
echo - Start Menu
echo - %INSTALL_DIR%\gui.py
echo.
echo To uninstall, run: %INSTALL_DIR%\uninstall.bat
echo.
pause
