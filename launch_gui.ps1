# Simple PowerShell script to launch Auto Mudfish GUI with admin privileges
# This version runs completely silently

param(
    [switch]$Force
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin -and -not $Force) {
    # Restart with elevation (completely hidden)
    Start-Process PowerShell -Verb RunAs -ArgumentList "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Force"
    exit
}

# Change to the script directory
Set-Location $PSScriptRoot

# Run the GUI (completely hidden)
Start-Process python -ArgumentList "gui.py" -WindowStyle Hidden
