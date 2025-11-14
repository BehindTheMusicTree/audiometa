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
    [string]::IsNullOrEmpty($PINNED_BWFMETAEDIT) -or
    [string]::IsNullOrEmpty($PINNED_EXIFTOOL)) {
    Write-Host "ERROR: Failed to load all required versions from system-dependencies.toml"
    Write-Host "Loaded versions:"
    Write-Host "  PINNED_FFMPEG=$PINNED_FFMPEG"
    Write-Host "  PINNED_FLAC=$PINNED_FLAC"
    Write-Host "  PINNED_MEDIAINFO=$PINNED_MEDIAINFO"
    Write-Host "  PINNED_ID3V2=$PINNED_ID3V2"
    Write-Host "  PINNED_BWFMETAEDIT=$PINNED_BWFMETAEDIT"
    Write-Host "  PINNED_EXIFTOOL=$PINNED_EXIFTOOL"
    exit 1
}

Write-Host "Installing pinned package versions..."

# Chocolatey version pinning format: choco install package --version=1.2.3
# Check exit code after each installation (choco doesn't throw exceptions)
$failedPackages = @()
$wslRequiredPackages = @()  # Track packages that require WSL

function Install-ChocoPackage {
    param(
        [string]$PackageName,
        [string]$Version
    )

    # Check if package is already installed
    $installedPackage = choco list $PackageName --local-only --exact 2>&1 | Select-String -Pattern "^$PackageName\s+(\S+)" | ForEach-Object { $_.Matches[0].Groups[1].Value }

    if ($installedPackage) {
        if ($installedPackage -eq $Version) {
            Write-Host "$PackageName $installedPackage already installed (matches pinned version $Version)"
            return $true
        } else {
            Write-Host "Removing existing $PackageName version $installedPackage (installing pinned version $Version)..."
            choco uninstall $PackageName -y 2>&1 | Out-Null
        }
    }

    Write-Host "Installing $PackageName..."
    & choco install $PackageName --version=$Version -y 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        return $false
    }
    return $true
}

if (-not (Install-ChocoPackage "ffmpeg" $PINNED_FFMPEG)) {
    $failedPackages += "ffmpeg"
}

if (-not (Install-ChocoPackage "flac" $PINNED_FLAC)) {
    $failedPackages += "flac"
}

if (-not (Install-ChocoPackage "mediainfo" $PINNED_MEDIAINFO)) {
    $failedPackages += "mediainfo"
}

# id3v2: Required for tests but not available in Chocolatey
# Install via WSL (Windows Subsystem for Linux) since id3v2 is a Linux tool
Write-Host "Installing id3v2 via WSL..."

# Check if WSL is installed and Ubuntu distribution is available
$wslInstalled = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $wslInstalled) {
    Write-Host "WSL not found. Installing WSL..."
    # Enable WSL feature
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart -ErrorAction SilentlyContinue
    # Install WSL (suppress output but capture errors)
    wsl --install -d Ubuntu 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install WSL. id3v2 requires WSL on Windows."
        Write-Host "Please install WSL manually: wsl --install"
        Write-Host "Or enable WSL feature: Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux"
        $failedPackages += "id3v2"
        $wslRequiredPackages += "id3v2"
    } else {
        Write-Host "WSL installed. Please restart and run this script again, or run: wsl --update"
        Write-Host "Then install id3v2 manually in WSL: wsl sudo apt-get update && wsl sudo apt-get install -y id3v2=$PINNED_ID3V2"
        exit 1
    }
}

# Check if Ubuntu distribution is available in WSL
$ubuntuAvailable = wsl -l -q 2>&1 | Select-String -Pattern "Ubuntu"
if (-not $ubuntuAvailable) {
    Write-Host "Ubuntu distribution not found in WSL. Installing Ubuntu..."
    wsl --install -d Ubuntu 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Ubuntu in WSL."
        Write-Host "Please install Ubuntu manually: wsl --install -d Ubuntu"
        Write-Host "Note: WSL installation may require elevated privileges or a system restart."
        Write-Host "Skipping id3v2 installation (requires WSL Ubuntu)."
        $failedPackages += "id3v2"
        $wslRequiredPackages += "id3v2"
    } else {
        Write-Host "Ubuntu installed. Please restart and run this script again."
        exit 1
    }
}

# Verify Ubuntu is actually available and working before proceeding
if ($failedPackages -notcontains "id3v2") {
    # Double-check Ubuntu is available by trying to list distributions
    $wslListOutput = wsl -l -q 2>&1
    $ubuntuAvailable = $wslListOutput | Select-String -Pattern "Ubuntu"
    if (-not $ubuntuAvailable) {
        Write-Host "ERROR: Ubuntu distribution not available in WSL after installation attempt."
        Write-Host "WSL output: $wslListOutput"
        Write-Host "Skipping id3v2 installation (requires WSL Ubuntu)."
        $failedPackages += "id3v2"
        $wslRequiredPackages += "id3v2"
    } else {
        # Install id3v2 in WSL Ubuntu with pinned version using shared script
        Write-Host "Installing id3v2 version $PINNED_ID3V2 in WSL Ubuntu..."

        # Convert Windows script path to WSL path
        $wslScriptPath = wsl wslpath -a "$SCRIPT_DIR\install-id3v2-linux.sh" 2>&1
        if ($LASTEXITCODE -ne 0) {
            # Fallback: construct WSL path manually if wslpath fails
            $wslScriptPath = $SCRIPT_DIR -replace '^([A-Z]):', '/mnt/$1' -replace '\\', '/'
            $wslScriptPath = "$wslScriptPath/install-id3v2-linux.sh"
        }

        # Call shared installation script via WSL
        wsl bash "$wslScriptPath" "$PINNED_ID3V2" 2>&1 | Out-Host
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to install id3v2 version $PINNED_ID3V2 in WSL."
            $failedPackages += "id3v2"
        }
    }
}

# Create wrapper script to make id3v2 accessible from Windows (if installation succeeded)
if ($failedPackages -notcontains "id3v2") {
    $wrapperDir = "C:\Program Files\id3v2-wrapper"
    New-Item -ItemType Directory -Force -Path $wrapperDir | Out-Null
    $wrapperScript = @"
@echo off
wsl id3v2 %*
"@
    $wrapperScript | Out-File -FilePath "$wrapperDir\id3v2.bat" -Encoding ASCII
    if ($env:GITHUB_PATH) {
        echo "$wrapperDir" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
    }
}

# Check if any packages failed
if ($failedPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to install the following packages: $($failedPackages -join ', ')"
    Write-Host ""

    # Separate WSL-required packages from version-related failures
    $versionRelatedFailures = $failedPackages | Where-Object { $wslRequiredPackages -notcontains $_ }
    $wslRelatedFailures = $failedPackages | Where-Object { $wslRequiredPackages -contains $_ }

    if ($versionRelatedFailures.Count -gt 0) {
        Write-Host "Version-related failures (Chocolatey packages):"
        foreach ($package in $versionRelatedFailures) {
            Write-Host "  - ${package}: Pinned version may not be available in Chocolatey"
        }
        Write-Host ""
        Write-Host "To fix:"
        Write-Host "  1. Check available versions: choco search <package> --exact"
        Write-Host "  2. Update system-dependencies.toml with correct versions"
        Write-Host ""
    }

    if ($wslRelatedFailures.Count -gt 0) {
        Write-Host "WSL-required packages (require Windows Subsystem for Linux):"
        foreach ($package in $wslRelatedFailures) {
            Write-Host "  - ${package}: Requires WSL Ubuntu to be installed"
        }
        Write-Host ""
        Write-Host "To fix:"
        Write-Host "  1. Install WSL: wsl --install -d Ubuntu"
        Write-Host "  2. Or enable WSL feature: Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux"
        Write-Host "  3. Restart your computer if prompted"
        Write-Host "  4. Run this script again"
        Write-Host ""
        Write-Host "Note: WSL installation may require elevated privileges or a system restart."
        Write-Host "      In CI environments, ensure WSL is pre-installed or use a runner with WSL support."
        Write-Host ""
    }

    exit 1
}

Write-Host "Installing bwfmetaedit (pinned version)..."

# Pinned version from system-dependencies.toml
$version = $PINNED_BWFMETAEDIT
$installDir = "C:\Program Files\BWFMetaEdit"
$exePath = "$installDir\bwfmetaedit.exe"

# Check if bwfmetaedit is already installed
$needInstall = $true
if (Test-Path $exePath) {
    try {
        $installedVersionOutput = & $exePath --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $installedVersion = $installedVersionOutput | Select-String -Pattern '(\d+\.\d+\.\d+)' | ForEach-Object { $_.Matches[0].Value }
            if ($installedVersion) {
                $installedMajorMinor = ($installedVersion -split '\.')[0..1] -join '.'
                $pinnedMajorMinor = ($version -split '\.')[0..1] -join '.'

                if ($installedMajorMinor -eq $pinnedMajorMinor) {
                    Write-Host "bwfmetaedit $installedVersion already installed (matches pinned version $version)"
                    $needInstall = $false
                } else {
                    Write-Host "Removing existing bwfmetaedit version $installedVersion (installing pinned version $version)..."
                    Remove-Item -Path $exePath -Force -ErrorAction SilentlyContinue
                    if (Test-Path $installDir) {
                        $dirContents = Get-ChildItem -Path $installDir -ErrorAction SilentlyContinue
                        if (-not $dirContents) {
                            Remove-Item -Path $installDir -Force -ErrorAction SilentlyContinue
                        }
                    }
                }
            }
        }
    } catch {
        Write-Host "bwfmetaedit installed but version could not be determined, removing..."
        Remove-Item -Path $exePath -Force -ErrorAction SilentlyContinue
        if (Test-Path $installDir) {
            $dirContents = Get-ChildItem -Path $installDir -ErrorAction SilentlyContinue
            if (-not $dirContents) {
                Remove-Item -Path $installDir -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Install if needed
if ($needInstall) {
    $url = "https://mediaarea.net/download/binary/bwfmetaedit/${version}/BWFMetaEdit_CLI_${version}_Windows_x64.zip"
    $tempDir = "$env:TEMP\bwfmetaedit"

    try {
        Write-Host "Downloading BWF MetaEdit..."
        New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
        Invoke-WebRequest -Uri $url -OutFile "$tempDir\bwfmetaedit.zip" -UseBasicParsing

        Write-Host "Extracting..."
        Expand-Archive -Path "$tempDir\bwfmetaedit.zip" -DestinationPath $tempDir -Force

        Write-Host "Installing..."
        New-Item -ItemType Directory -Force -Path $installDir | Out-Null
        $exe = Get-ChildItem -Path $tempDir -Filter "bwfmetaedit.exe" -Recurse | Select-Object -First 1
        if (-not $exe) {
            throw "bwfmetaedit.exe not found in downloaded archive"
        }
        Copy-Item -Path $exe.FullName -Destination $exePath -Force

        Write-Host "Adding to PATH..."
        if ($env:GITHUB_PATH) {
            echo "$installDir" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
        }

        Write-Host "Cleanup..."
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "bwfmetaedit $version installed successfully"
    } catch {
        Write-Host "ERROR: Failed to install bwfmetaedit: $_"
        exit 1
    }
}

Write-Host "Installing exiftool (pinned version)..."

# Pinned version from system-dependencies.toml
$exiftoolVersion = $PINNED_EXIFTOOL
$exiftoolInstallDir = "C:\Program Files\ExifTool"
$exiftoolExePath = "$exiftoolInstallDir\exiftool.exe"

# Check if exiftool is already installed
$needInstallExiftool = $true
if (Test-Path $exiftoolExePath) {
    try {
        $installedVersionOutput = & $exiftoolExePath -ver 2>&1
        if ($LASTEXITCODE -eq 0) {
            $installedVersion = $installedVersionOutput.Trim()
            if ($installedVersion) {
                $installedMajorMinor = ($installedVersion -split '\.')[0..1] -join '.'
                $pinnedMajorMinor = ($exiftoolVersion -split '\.')[0..1] -join '.'

                if ($installedMajorMinor -eq $pinnedMajorMinor) {
                    Write-Host "exiftool $installedVersion already installed (matches pinned version $exiftoolVersion)"
                    $needInstallExiftool = $false
                } else {
                    Write-Host "Removing existing exiftool version $installedVersion (installing pinned version $exiftoolVersion)..."
                    Remove-Item -Path $exiftoolExePath -Force -ErrorAction SilentlyContinue
                    if (Test-Path $exiftoolInstallDir) {
                        $dirContents = Get-ChildItem -Path $exiftoolInstallDir -ErrorAction SilentlyContinue
                        if (-not $dirContents) {
                            Remove-Item -Path $exiftoolInstallDir -Force -ErrorAction SilentlyContinue
                        }
                    }
                }
            }
        }
    } catch {
        Write-Host "exiftool installed but version could not be determined, removing..."
        Remove-Item -Path $exiftoolExePath -Force -ErrorAction SilentlyContinue
        if (Test-Path $exiftoolInstallDir) {
            $dirContents = Get-ChildItem -Path $exiftoolInstallDir -ErrorAction SilentlyContinue
            if (-not $dirContents) {
                Remove-Item -Path $exiftoolInstallDir -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Install if needed
if ($needInstallExiftool) {
    $url = "https://exiftool.org/exiftool-${exiftoolVersion}.zip"
    $tempDir = "$env:TEMP\exiftool"

    try {
        Write-Host "Downloading ExifTool..."
        New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
        Invoke-WebRequest -Uri $url -OutFile "$tempDir\exiftool.zip" -UseBasicParsing

        Write-Host "Extracting..."
        Expand-Archive -Path "$tempDir\exiftool.zip" -DestinationPath $tempDir -Force

        Write-Host "Installing..."
        New-Item -ItemType Directory -Force -Path $exiftoolInstallDir | Out-Null
        # ExifTool Windows archive contains exiftool(-k).exe which needs to be renamed
        $exe = Get-ChildItem -Path $tempDir -Filter "exiftool*.exe" -Recurse | Select-Object -First 1
        if (-not $exe) {
            throw "exiftool.exe not found in downloaded archive"
        }
        # Copy and rename to exiftool.exe
        Copy-Item -Path $exe.FullName -Destination $exiftoolExePath -Force
        # Also copy the lib directory if it exists (contains exiftool_files)
        $libDir = Get-ChildItem -Path $tempDir -Directory -Filter "*lib*" -Recurse | Select-Object -First 1
        if ($libDir) {
            Copy-Item -Path $libDir.FullName -Destination "$exiftoolInstallDir\lib" -Recurse -Force
        }

        Write-Host "Adding to PATH..."
        if ($env:GITHUB_PATH) {
            echo "$exiftoolInstallDir" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
        }

        Write-Host "Cleanup..."
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "exiftool $exiftoolVersion installed successfully"
    } catch {
        Write-Host "ERROR: Failed to install exiftool: $_"
        exit 1
    }
}

Write-Host "Verifying installed tools are available in PATH..."
$missingTools = @()
$tools = @("ffprobe", "flac", "metaflac", "mediainfo", "id3v2", "exiftool")
foreach ($tool in $tools) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        $missingTools += $tool
    }
}

if ($missingTools.Count -ne 0) {
    Write-Host "ERROR: The following tools are not available in PATH after installation:"
    foreach ($tool in $missingTools) {
        Write-Host "  - $tool"
    }
    Write-Host ""
    Write-Host "Installation may have failed. Check the output above for errors."
    Write-Host "Note: PATH changes may require a new shell session to take effect."
    exit 1
}

Write-Host "All system dependencies installed successfully!"


