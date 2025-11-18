param(
    [string]$InstallDir = "$env:USERPROFILE\devctl"
)

Write-Host "Installing devctl to: $InstallDir" -ForegroundColor Cyan

$Source = $PSScriptRoot

# --- Ensure InstallDir is a directory ---
if (Test-Path $InstallDir) {
    $item = Get-Item $InstallDir
    if (-not $item.PSIsContainer) {
        Write-Host "Removing conflicting file: $InstallDir"
        Remove-Item -Force $InstallDir
        New-Item -ItemType Directory -Path $InstallDir | Out-Null
    }
} else {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}

# --- Fix conflicting leaf files inside directories ---
$folders = @("bin", "env", "scripts")
foreach ($folder in $folders) {
    $target = Join-Path $InstallDir $folder
    if ((Test-Path $target) -and -not (Get-Item $target).PSIsContainer) {
        Write-Host "Removing invalid file blocking folder: $target"
        Remove-Item -Force $target
    }
}

# --- Copy files safely ---
Write-Host "Copying devctl files..."
Copy-Item -Path "$Source\*" -Destination $InstallDir -Recurse -Force

# --- Add to PATH (persistent via registry) ---
$regPath = "HKCU:\Environment"
$currentPath = (Get-ItemProperty -Path $regPath -Name PATH -ErrorAction SilentlyContinue).PATH

if ($null -eq $currentPath) {
    $currentPath = ""
}

if ($currentPath -notlike "*$InstallDir*") {
    $newPath = $currentPath.TrimEnd(";") + ";$InstallDir"
    Set-ItemProperty -Path $regPath -Name PATH -Value $newPath
    Write-Host "Added $InstallDir to PATH (registry updated)" -ForegroundColor Green
} else {
    Write-Host "PATH already contains $InstallDir"
}

# --- Update current session PATH immediately ---
$env:PATH = "$env:PATH;$InstallDir"

# --- Verify ---
if (Get-Command devctl.bat -ErrorAction SilentlyContinue) {
    Write-Host "`ndevctl is now available in this terminal session." -ForegroundColor Green
} else {
    Write-Host "`nWARNING: devctl NOT found in session PATH. Restart terminal." -ForegroundColor Yellow
}

Write-Host "`nInstall complete!"
Write-Host "Restart your terminal and run: devctl --version"
