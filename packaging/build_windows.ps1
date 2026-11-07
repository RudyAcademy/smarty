# Builds a frozen Smarty.exe with PyInstaller (one-dir, windowed, no console).
# Run from the project root (C:\TowerHill\Smarty) in the project's venv:
#   .\.venv\Scripts\Activate.ps1
#   .\packaging\build_windows.ps1
# Output: dist\Smarty\Smarty.exe plus its _internal\ support files.
# This script only builds locally. It never copies anything to T:\.

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

python -m PyInstaller --name Smarty --onedir --windowed --noconfirm `
    --paths src `
    smarty_launcher.py

Write-Host "Built: dist\Smarty\Smarty.exe"
