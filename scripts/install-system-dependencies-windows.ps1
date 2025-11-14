# Install system dependencies for Windows CI
# Pinned versions from system-dependencies.toml (fails if not available, no fallback)
# See system-dependencies.toml for version configuration

$ErrorActionPreference = "Stop"

# Load pinned versions from system-dependencies.toml
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$versionOutput = python3 "$SCRIPT_DIR\ci\load-system-dependency-versions.py" powershell
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($versionOutput)) {
    Write-Host "ERROR: Failed to load versions from system-dependencies.toml"
    exit 1
}
# Join array output into single string and execute
$versionOutputString = $versionOutput -join "`n"
Invoke-Expression $versionOutputString

# Verify versions were loaded
if ([string]::IsNullOrEmpty($PINNED_FFMPEG) -or
    [string]::IsNullOrEmpty($PINNED_FLAC) -or
    [string]::IsNullOrEmpty($PINNED_MEDIAINFO) -or
    [string]::IsNullOrEmpty($PINNED_ID3V2) -or
    [string]::IsNullOrEmpty($PINNED_BWFMETAEDIT)) {
    Write-Host "ERROR: Failed to load all required versions from system-dependencies.toml"
    Write-Host "Loaded versions:"
    Write-Host "  PINNED_FFMPEG=$PINNED_FFMPEG"
    Write-Host "  PINNED_FLAC=$PINNED_FLAC"
    Write-Host "  PINNED_MEDIAINFO=$PINNED_MEDIAINFO"
    Write-Host "  PINNED_ID3V2=$PINNED_ID3V2"
    Write-Host "  PINNED_BWFMETAEDIT=$PINNED_BWFMETAEDIT"
    exit 1
}

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


