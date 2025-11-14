# Install bwfmetaedit for Windows CI
# Pinned version: 24.05 (fails if not available, no fallback)
# See .github/system-dependencies.toml for version configuration

$ErrorActionPreference = "Stop"

# Pinned version: 24.05 (from .github/system-dependencies.toml)
$version = "24.05"
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

Write-Host "BWF MetaEdit installed successfully!"


