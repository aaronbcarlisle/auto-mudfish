# Simple launcher that works reliably
param(
    [switch]$Force
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin -and -not $Force) {
    # Restart with elevation
    Start-Process PowerShell -Verb RunAs -ArgumentList "-File `"$PSCommandPath`" -Force"
    exit
}

# We're running as admin, launch the GUI
$scriptDir = Split-Path -Parent $PSCommandPath
Set-Location $scriptDir

# Launch GUI in a new window (not hidden so we can see if it works)
Start-Process python -ArgumentList "gui.py"
