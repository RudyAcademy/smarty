# Creates a desktop shortcut named "Smarty" that launches the frozen build
# (dist\Smarty\Smarty.exe). Per-user, no admin required. The shortcut always
# targets the local build -- never a path on T:\.
#
# Usage (from the project root, after build_windows.ps1 has produced dist\Smarty):
#   .\packaging\create_shortcut.ps1
# Optional: -InstallDir to copy the built app out of dist\ into a per-user
# Programs folder first (recommended for a "real" install vs. a dev build).

param(
    [string]$InstallDir = "$env:LocalAppData\Programs\Smarty"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DistDir = Join-Path $ProjectRoot "dist\Smarty"

if (-not (Test-Path (Join-Path $DistDir "Smarty.exe"))) {
    throw "dist\Smarty\Smarty.exe not found. Run packaging\build_windows.ps1 first."
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Path (Join-Path $DistDir "*") -Destination $InstallDir -Recurse -Force

$TargetExe = Join-Path $InstallDir "Smarty.exe"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Smarty.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetExe
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Smarty - Tower Hill business ideas review"
$Shortcut.Save()

Write-Host "Installed to: $InstallDir"
Write-Host "Shortcut created: $ShortcutPath"
