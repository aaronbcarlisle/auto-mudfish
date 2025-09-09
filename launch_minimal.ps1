# Minimal launcher for Auto Mudfish GUI (minimized window)
param(
    [switch]$Force
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin -and -not $Force) {
    # Restart with elevation
    Start-Process PowerShell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -Force"
    exit
}

# We're running as admin, launch the GUI
$scriptDir = Split-Path -Parent $PSCommandPath
Set-Location $scriptDir

# Launch GUI and minimize this window
Start-Process python -ArgumentList "gui.py"

# Minimize this PowerShell window
Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        [DllImport("kernel32.dll")]
        public static extern IntPtr GetConsoleWindow();
    }
"@

$consoleWindow = [Win32]::GetConsoleWindow()
[Win32]::ShowWindow($consoleWindow, 6) # SW_MINIMIZE
