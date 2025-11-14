# BWF MetaEdit Installation Script for Windows
# This script downloads and installs BWF MetaEdit from MediaArea

$ErrorActionPreference = "Stop"

# Configuration
$downloadUrl = "https://mediaarea.net/download/binary/bwfmetaedit/24.05/BWFMetaEdit_CLI_24.05_Windows_x64.zip"
$tempDir = "$env:TEMP\bwfmetaedit"
$installDir = "$env:ProgramFiles\BWFMetaEdit"
$zipFile = "$tempDir\bwfmetaedit.zip"

Write-Host "BWF MetaEdit Installation Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Create temp directory
Write-Host "Creating temporary directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Download BWF MetaEdit
Write-Host "Downloading BWF MetaEdit from MediaArea..." -ForegroundColor Yellow
Write-Host "URL: $downloadUrl" -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "Download completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error downloading BWF MetaEdit: $_" -ForegroundColor Red
    exit 1
}

# Extract archive
Write-Host "Extracting archive..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipFile -DestinationPath $tempDir -Force
    Write-Host "Extraction completed!" -ForegroundColor Green
} catch {
    Write-Host "Error extracting archive: $_" -ForegroundColor Red
    exit 1
}

# Create installation directory
Write-Host "Creating installation directory: $installDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

# Copy executable
Write-Host "Installing BWF MetaEdit..." -ForegroundColor Yellow
$exePath = Get-ChildItem -Path $tempDir -Filter "bwfmetaedit.exe" -Recurse | Select-Object -First 1
if ($exePath) {
    Copy-Item -Path $exePath.FullName -Destination "$installDir\bwfmetaedit.exe" -Force
    Write-Host "BWF MetaEdit installed to: $installDir" -ForegroundColor Green
} else {
    Write-Host "Error: Could not find bwfmetaedit.exe in the archive" -ForegroundColor Red
    exit 1
}

# Add to PATH
Write-Host "Adding to system PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($currentPath -notlike "*$installDir*") {
    try {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$installDir",
            "Machine"
        )
        Write-Host "Added to system PATH successfully!" -ForegroundColor Green
        Write-Host "Note: You may need to restart your terminal for PATH changes to take effect." -ForegroundColor Yellow
    } catch {
        Write-Host "Warning: Could not add to system PATH automatically." -ForegroundColor Yellow
        Write-Host "Please add manually: $installDir" -ForegroundColor Yellow
    }
} else {
    Write-Host "Already in system PATH" -ForegroundColor Green
}

# Cleanup
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path $tempDir -Recurse -Force

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
try {
    $version = & "$installDir\bwfmetaedit.exe" --version 2>&1
    Write-Host "Installation successful!" -ForegroundColor Green
    Write-Host "BWF MetaEdit version: $version" -ForegroundColor Cyan
} catch {
    Write-Host "Installed, but could not verify. Try running: bwfmetaedit --version" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "You may need to restart your terminal or PowerShell session." -ForegroundColor Yellow
