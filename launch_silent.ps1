# Silent launcher for Auto Mudfish GUI
param(
    [switch]$Force
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin -and -not $Force) {
    # Restart with elevation (visible for elevation, then hidden)
    Start-Process PowerShell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -Force"
    exit
}

# We're running as admin, launch the GUI silently
$scriptDir = Split-Path -Parent $PSCommandPath
Set-Location $scriptDir

# Launch GUI using pythonw (no console window)
Start-Process pythonw -ArgumentList "gui.py"

exit
