# PowerShell script to run Auto Mudfish with administrator privileges
param(
    [switch]$Force
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin -and -not $Force) {
    Write-Host "This application requires administrator privileges to launch Mudfish." -ForegroundColor Yellow
    Write-Host "Restarting with elevation..." -ForegroundColor Green
    
    # Get the full path to the script directory
    $scriptDir = Split-Path -Parent $PSCommandPath
    
    # Restart with elevation, passing the script directory
    Start-Process PowerShell -Verb RunAs -ArgumentList "-WindowStyle Hidden -File `"$PSCommandPath`" -Force -ScriptDir `"$scriptDir`""
    exit
}

# Get script directory from parameter or use current
if ($args -contains "-ScriptDir") {
    $scriptDirIndex = [array]::IndexOf($args, "-ScriptDir")
    if ($scriptDirIndex -ge 0 -and $scriptDirIndex -lt $args.Length - 1) {
        $scriptDir = $args[$scriptDirIndex + 1]
    }
} else {
    $scriptDir = $PSScriptRoot
}

# Change to the script directory
Set-Location $scriptDir

# Run the GUI
Start-Process python -ArgumentList "gui.py" -WindowStyle Hidden
