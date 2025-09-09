# Simple PowerShell script to run Auto Mudfish GUI
# This version doesn't require elevation - use for testing

# Get the script directory
$scriptDir = Split-Path -Parent $PSCommandPath

# Change to the script directory
Set-Location $scriptDir

Write-Host "Starting Auto Mudfish GUI..." -ForegroundColor Green

# Run the GUI
try {
    Start-Process python -ArgumentList "src/gui/gui.py"
    Write-Host "GUI started successfully!" -ForegroundColor Green
    Write-Host "The GUI window should appear shortly." -ForegroundColor Cyan
} catch {
    Write-Host "Error starting GUI: $_" -ForegroundColor Red
    Write-Host "Make sure Python and dependencies are installed." -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
}
