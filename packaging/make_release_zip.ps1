# Zips the built dist\Smarty folder into Smarty_vX.Y.Z.zip and writes a
# local latest.json manifest (version, zip, sha256, windows_installer,
# built_on) once the zip's hash is confirmed.
#
# This script NEVER copies anything to T:\TowerHill\Sparky\Installers.
# The live T: mapping has not been verified from this build machine, and
# publishing a build is a decision for Rudy/Lumi to make deliberately on
# a machine that can see the real share -- not something a build script
# should do on its own.
#
# Usage:
#   .\packaging\make_release_zip.ps1 -Version 0.1.0

param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [string]$OutDir = "release"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DistDir = Join-Path $ProjectRoot "dist\Smarty"
$OutPath = Join-Path $ProjectRoot $OutDir

if (-not (Test-Path (Join-Path $DistDir "Smarty.exe"))) {
    throw "dist\Smarty\Smarty.exe not found. Run packaging\build_windows.ps1 first."
}

New-Item -ItemType Directory -Force -Path $OutPath | Out-Null
$ZipName = "Smarty_v$Version.zip"
$ZipPath = Join-Path $OutPath $ZipName

if (Test-Path $ZipPath) { Remove-Item $ZipPath }
Compress-Archive -Path (Join-Path $DistDir "*") -DestinationPath $ZipPath

$Hash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToLower()

$Manifest = [ordered]@{
    version           = $Version
    zip               = $ZipName
    sha256            = $Hash
    windows_installer = $false
    built_on          = "windows"
}
$ManifestPath = Join-Path $OutPath "latest.json"
$Manifest | ConvertTo-Json | Set-Content -Path $ManifestPath -Encoding utf8

Write-Host "Zip:      $ZipPath"
Write-Host "SHA-256:  $Hash"
Write-Host "Manifest: $ManifestPath"
Write-Host ""
Write-Host "Not copied anywhere else. To publish to the share, confirm the T:\ mapping" -ForegroundColor Yellow
Write-Host "yourself, then manually copy $ZipName and latest.json into" -ForegroundColor Yellow
Write-Host "T:\TowerHill\Sparky\Installers\ (zip first, then latest.json last)." -ForegroundColor Yellow
