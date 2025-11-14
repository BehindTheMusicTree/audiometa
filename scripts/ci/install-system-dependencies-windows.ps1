# Install system dependencies for Windows CI
# Pinned versions from system-dependencies.toml (fails if not available, no fallback)
# See system-dependencies.toml for version configuration

$ErrorActionPreference = "Stop"

# Load pinned versions from system-dependencies.toml
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$versionOutput = python3 "$SCRIPT_DIR\load-system-dependency-versions.py" powershell
Invoke-Expression $versionOutput

Write-Host "Installing pinned package versions..."

# Chocolatey version pinning format: choco install package --version=1.2.3
try {
    choco install ffmpeg --version=$PINNED_FFMPEG -y
    choco install flac --version=$PINNED_FLAC -y
    choco install mediainfo --version=$PINNED_MEDIAINFO -y
    choco install id3v2 --version=$PINNED_ID3V2 -y
} catch {
    Write-Host "ERROR: Pinned versions not available."
    Write-Host "Update system-dependencies.toml with correct versions."
    Write-Host "Check available versions with: choco search <package> --exact"
    exit 1
}

Write-Host "Installing bwfmetaedit (pinned version)..."

# Pinned version from system-dependencies.toml
$version = $PINNED_BWFMETAEDIT
$url = "https://mediaarea.net/download/binary/bwfmetaedit/${version}/BWFMetaEdit_CLI_${version}_Windows_x64.zip"
$tempDir = "$env:TEMP\bwfmetaedit"
$installDir = "C:\Program Files\BWFMetaEdit"

Write-Host "Downloading BWF MetaEdit..."
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Invoke-WebRequest -Uri $url -OutFile "$tempDir\bwfmetaedit.zip" -UseBasicParsing

Write-Host "Extracting..."
Expand-Archive -Path "$tempDir\bwfmetaedit.zip" -DestinationPath $tempDir -Force

Write-Host "Installing..."
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
$exe = Get-ChildItem -Path $tempDir -Filter "bwfmetaedit.exe" -Recurse | Select-Object -First 1
Copy-Item -Path $exe.FullName -Destination "$installDir\bwfmetaedit.exe" -Force

Write-Host "Adding to PATH..."
echo "$installDir" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append

Write-Host "Cleanup..."
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "All system dependencies installed successfully!"


