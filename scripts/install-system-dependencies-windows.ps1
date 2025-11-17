# Install system dependencies for Windows CI
# Pinned versions from system-dependencies.toml (fails if not available, no fallback)
# See system-dependencies.toml for version configuration

$ErrorActionPreference = "Stop"

# Load pinned versions from system-dependencies.toml
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$versionOutput = python3 "$SCRIPT_DIR\load-system-dependency-versions.py" powershell
if ($LASTEXITCODE -ne 0) {
    Write-Error "ERROR: Failed to load versions from system-dependencies.toml (exit code: $LASTEXITCODE)"
    exit 1
}
# Convert output to array of lines (handles both string and array output)
if ($versionOutput -is [string]) {
    $versionLines = $versionOutput -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
}
else {
    $versionLines = $versionOutput | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
}
if ($null -eq $versionLines -or $versionLines.Count -eq 0) {
    Write-Error "ERROR: No version output received from load-system-dependency-versions.py"
    exit 1
}
# Parse output and set variables safely (replaces Invoke-Expression)
foreach ($line in $versionLines) {
    $trimmedLine = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmedLine) -or $trimmedLine.StartsWith('#')) {
        continue
    }
    # Parse lines like: $PINNED_FFMPEG = "7.1.1"
    if ($trimmedLine -match '\$([A-Z_]+)\s*=\s*"([^"]+)"') {
        $varName = $matches[1]
        $varValue = $matches[2]
        Set-Variable -Name $varName -Value $varValue -Scope Script
    }
}

# Verify versions were loaded
if ([string]::IsNullOrEmpty($PINNED_FFMPEG) -or
    [string]::IsNullOrEmpty($PINNED_FLAC) -or
    [string]::IsNullOrEmpty($PINNED_MEDIAINFO) -or
    [string]::IsNullOrEmpty($PINNED_ID3V2) -or
    [string]::IsNullOrEmpty($PINNED_BWFMETAEDIT) -or
    [string]::IsNullOrEmpty($PINNED_EXIFTOOL)) {
    Write-Error "ERROR: Failed to load all required versions from system-dependencies.toml"
    Write-Output "Loaded versions:"
    Write-Output "  PINNED_FFMPEG=$PINNED_FFMPEG"
    Write-Output "  PINNED_FLAC=$PINNED_FLAC"
    Write-Output "  PINNED_MEDIAINFO=$PINNED_MEDIAINFO"
    Write-Output "  PINNED_ID3V2=$PINNED_ID3V2"
    Write-Output "  PINNED_BWFMETAEDIT=$PINNED_BWFMETAEDIT"
    Write-Output "  PINNED_EXIFTOOL=$PINNED_EXIFTOOL"
    exit 1
}

Write-Output "Installing pinned package versions..."

# Check if running in CI environment
$isCI = $env:CI -eq "true" -or $env:GITHUB_ACTIONS -eq "true" -or $env:TF_BUILD -eq "true"

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
            Write-Output "$PackageName $installedPackage already installed (matches pinned version $Version)"
            return $true
        }
        else {
            Write-Output "Removing existing $PackageName version $installedPackage (installing pinned version $Version)..."
            choco uninstall $PackageName -y 2>&1 | Out-Null
        }
    }

    Write-Output "Installing $PackageName..."
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

# mediainfo: Only needed for integration tests (verification), not e2e tests
# Skip installation on Windows CI since we only run e2e tests
if (-not $isCI) {
    if (-not (Install-ChocoPackage "mediainfo" $PINNED_MEDIAINFO)) {
        $failedPackages += "mediainfo"
    }
}
else {
    Write-Output "Skipping mediainfo installation (not needed for e2e tests on Windows CI)"
}

# id3v2: Optional on Windows CI (not needed for e2e tests)
# Install via WSL (Windows Subsystem for Linux) since id3v2 is a Linux tool
#
# Why skip WSL installation in CI:
# 1. Windows CI only runs e2e tests (unit/integration tests run on Ubuntu/macOS)
# 2. e2e tests don't use id3v2 (they use mutagen for MP3, metaflac for FLAC, bwfmetaedit for WAV)
# 3. WSL installation requires a system restart in most cases, which is not possible in CI
# 4. WSL installation adds significant complexity to CI setup (DISM, feature enabling, Ubuntu distro setup)
# 5. WSL installation attempts often fail in CI environments due to restart requirements and complexity
# 6. Version verification in pytest already skips id3v2 on Windows
#
# For local development: WSL installation is attempted if not in CI, allowing full test coverage
if ($isCI) {
    Write-Output "Skipping id3v2 installation (not needed for e2e tests on Windows CI)"
    $failedPackages += "id3v2"
    $wslRequiredPackages += "id3v2"
}
else {
    Write-Output "Installing id3v2 via WSL..."

    # Check if WSL is installed and Ubuntu distribution is available
    $wslInstalled = Get-Command wsl -ErrorAction SilentlyContinue
    if (-not $wslInstalled) {
        Write-Output "WSL not found. Attempting to install WSL..."

        # Enable WSL feature using DISM (more reliable, no restart required)
        Write-Output "Enabling WSL feature using DISM..."
        $dismOutput = dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /norestart 2>&1 | Out-String
        Write-Output "DISM output: $dismOutput"
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to enable WSL feature via DISM (exit code: $LASTEXITCODE). Trying alternative method..."
            # Fallback to Enable-WindowsOptionalFeature
            $enableResult = Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart -ErrorAction SilentlyContinue
            if ($LASTEXITCODE -ne 0 -and -not $enableResult) {
                Write-Warning "Failed to enable WSL feature. May require admin privileges or manual setup."
                Write-Output "Exit code: $LASTEXITCODE"
            }
        }
        else {
            Write-Output "WSL feature enabled successfully via DISM."
        }

        # Enable Virtual Machine Platform (required for WSL2, but WSL1 should work without it)
        Write-Output "Enabling Virtual Machine Platform feature..."
        $vmpOutput = dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /norestart 2>&1 | Out-String
        Write-Output "Virtual Machine Platform DISM output: $vmpOutput"

        # Try to install WSL and Ubuntu
        Write-Output "Installing WSL with Ubuntu..."
        $wslInstallOutput = wsl --install -d Ubuntu --no-distribution 2>&1 | Out-String
        Write-Output "WSL install output (--no-distribution): $wslInstallOutput"
        if ($LASTEXITCODE -ne 0) {
            # Try without --no-distribution flag (older WSL versions)
            Write-Output "Retrying WSL installation without --no-distribution flag..."
            $wslInstallOutput = wsl --install -d Ubuntu 2>&1 | Out-String
            Write-Output "WSL install output (standard): $wslInstallOutput"
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Output ""
            Write-Warning "WSL installation failed (exit code: $LASTEXITCODE)."
            Write-Output "This usually means WSL requires a system restart."
            Write-Output "Full WSL output: $wslInstallOutput"
            Write-Output ""
            Write-Output "id3v2 installation skipped. To install WSL manually:"
            Write-Output "  1. Run: wsl --install -d Ubuntu"
            Write-Output "  2. Restart your computer if prompted"
            Write-Output "  3. Run this script again"
            Write-Output ""
            # Don't exit - continue with other package installations
            $failedPackages += "id3v2"
            $wslRequiredPackages += "id3v2"
        }
        else {
            Write-Output "WSL installation initiated. Checking if Ubuntu is available..."
            # Wait a moment for WSL to initialize
            Start-Sleep -Seconds 5
            # Check if WSL is now available
            $wslCheck = Get-Command wsl -ErrorAction SilentlyContinue
            if (-not $wslCheck) {
                Write-Output ""
                Write-Warning "WSL installed but not available (may require restart)."
                Write-Output "WSL installation requires a system restart to be fully functional."
                Write-Output ""
                Write-Output "id3v2 installation skipped. Please restart your computer and run this script again."
                Write-Output ""
                # Don't exit - continue with other package installations
                $failedPackages += "id3v2"
                $wslRequiredPackages += "id3v2"
            }
        }
    }

    # Check if Ubuntu distribution is available in WSL
    $ubuntuAvailable = $false
    $wslCheck = Get-Command wsl -ErrorAction SilentlyContinue
    if ($wslCheck) {
        $wslListOutput = wsl -l -q 2>&1 | Out-String
        $ubuntuMatch = $wslListOutput | Select-String -Pattern "Ubuntu"
        $ubuntuAvailable = $null -ne $ubuntuMatch
    }

    if (-not $ubuntuAvailable) {
        Write-Output "Ubuntu distribution not found in WSL. Attempting to install Ubuntu..."

        # First, try to update WSL if available
        if ($wslCheck) {
            Write-Output "Updating WSL..."
            wsl --update 2>&1 | Out-Null
        }

        # Try to install Ubuntu distribution
        Write-Output "Installing Ubuntu distribution..."
        $ubuntuInstallOutput = wsl --install -d Ubuntu 2>&1 | Out-String
        $installExitCode = $LASTEXITCODE
        Write-Output "Ubuntu install command exit code: $installExitCode"
        Write-Output "Ubuntu install output: $ubuntuInstallOutput"

        # Check if installation succeeded or if Ubuntu is now available
        if ($installExitCode -eq 0) {
            Write-Output "Ubuntu installation command succeeded. Waiting for initialization..."
            Start-Sleep -Seconds 15
        }
        else {
            # Installation command failed, but Ubuntu might still be installing in background
            Write-Warning "Ubuntu install command failed (exit code: $installExitCode)"
            Write-Output "This may indicate that WSL requires a restart or Ubuntu installation failed."
            Write-Output "Waiting to check if Ubuntu becomes available..."
            Start-Sleep -Seconds 20
        }

        # Check again if Ubuntu is available
        Write-Output "Checking if Ubuntu is now available..."
        $wslListOutput = wsl -l -q 2>&1 | Out-String
        Write-Output "WSL list output: $wslListOutput"

        # Check if Ubuntu is in the list (case-insensitive, handle whitespace)
        $ubuntuMatch = $wslListOutput | Select-String -Pattern "Ubuntu" -CaseSensitive:$false
        $ubuntuInList = $null -ne $ubuntuMatch

        # Also check if installation output indicates success
        $installSucceeded = $ubuntuInstallOutput -match "Distribution successfully installed" -or $ubuntuInstallOutput -match "successfully installed"

        Write-Output "Ubuntu in WSL list: $ubuntuInList"
        Write-Output "Install output indicates success: $installSucceeded"

        if ($ubuntuInList -or $installSucceeded) {
            Write-Output "Ubuntu appears to be installed. Testing if it's functional..."
            # Try to run a simple command to see if Ubuntu works
            $testOutput = wsl -d Ubuntu echo "test" 2>&1 | Out-String
            Write-Output "Ubuntu test command output: $testOutput"
            Write-Output "Ubuntu test exit code: $LASTEXITCODE"

            if ($LASTEXITCODE -eq 0 -or $testOutput -match "test") {
                Write-Output "Ubuntu is working! Proceeding with id3v2 installation..."
                $ubuntuAvailable = $true
            }
            elseif ($installSucceeded) {
                Write-Warning "Ubuntu installation succeeded but may not be fully initialized."
                Write-Output "The OOBE (Out of Box Experience) setup may have failed, but Ubuntu is installed."
                Write-Output "Attempting to proceed anyway - id3v2 installation may work..."
                $ubuntuAvailable = $true
            }
            else {
                Write-Output "Ubuntu is listed but not responding. May need manual setup."
                $ubuntuAvailable = $false
            }
        }
        else {
            $ubuntuAvailable = $false
        }

        if (-not $ubuntuAvailable) {
            Write-Output ""
            Write-Warning "Ubuntu distribution not available after installation attempt."
            Write-Output "WSL installation on Windows typically requires a system restart."
            Write-Output ""
            Write-Output "id3v2 installation skipped. To install manually:"
            Write-Output "  1. Run: wsl --install -d Ubuntu"
            Write-Output "  2. Restart your computer if prompted"
            Write-Output "  3. Run this script again"
            Write-Output ""
            # Don't exit - continue with other package installations
            $failedPackages += "id3v2"
            $wslRequiredPackages += "id3v2"
        }
        else {
            Write-Output "Ubuntu distribution is now available!"
        }
    }
}

# Verify Ubuntu is actually available and working before proceeding (only if not in CI)
if (-not $isCI -and $failedPackages -notcontains "id3v2") {
    # Double-check Ubuntu is available by trying to list distributions
    $wslListOutput = wsl -l -q 2>&1 | Out-String
    $ubuntuMatch = $wslListOutput | Select-String -Pattern "Ubuntu"
    $ubuntuAvailable = $null -ne $ubuntuMatch
    if (-not $ubuntuAvailable) {
        Write-Error "Ubuntu distribution not available in WSL after installation attempt."
        Write-Output "WSL output: $wslListOutput"
        Write-Output "Skipping id3v2 installation (requires WSL Ubuntu)."
        $failedPackages += "id3v2"
        $wslRequiredPackages += "id3v2"
    }
    else {
        # Install id3v2 in WSL Ubuntu with pinned version using shared script
        Write-Output "Installing id3v2 version $PINNED_ID3V2 in WSL Ubuntu..."

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
            Write-Error "Failed to install id3v2 version $PINNED_ID3V2 in WSL."
            $failedPackages += "id3v2"
        }
    }
}

# Create wrapper script to make id3v2 accessible from Windows (if installation succeeded, and not in CI)
if (-not $isCI -and $failedPackages -notcontains "id3v2") {
    $wrapperDir = "C:\Program Files\id3v2-wrapper"
    New-Item -ItemType Directory -Force -Path $wrapperDir | Out-Null
    $wrapperScript = @"
@echo off
wsl id3v2 %*
"@
    $wrapperScript | Out-File -FilePath "$wrapperDir\id3v2.bat" -Encoding ASCII
    if ($env:GITHUB_PATH) {
        Write-Output "$wrapperDir" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
    }
}

# Check if any packages failed
if ($failedPackages.Count -gt 0) {
    # Separate WSL-required packages from version-related failures
    $versionRelatedFailures = $failedPackages | Where-Object { $wslRequiredPackages -notcontains $_ }
    $wslRelatedFailures = $failedPackages | Where-Object { $wslRequiredPackages -contains $_ }

    Write-Output ""

    # Version-related failures always exit early (can't install other packages)
    # WSL-related failures: continue installing other packages, then fail at the end
    if ($versionRelatedFailures.Count -gt 0) {
        Write-Error "Failed to install the following packages: $($failedPackages -join ', ')"
        Write-Output ""

        if ($versionRelatedFailures.Count -gt 0) {
            Write-Output "Version-related failures (Chocolatey packages):"
            foreach ($package in $versionRelatedFailures) {
                Write-Output "  - ${package}: Pinned version may not be available in Chocolatey"
            }
            Write-Output ""
            Write-Output "To fix:"
            Write-Output "  1. Check available versions: choco search <package> --exact"
            Write-Output "  2. Update system-dependencies.toml with correct versions"
            Write-Output ""
        }

        if ($wslRelatedFailures.Count -gt 0) {
            Write-Output "WSL-required packages (require Windows Subsystem for Linux):"
            foreach ($package in $wslRelatedFailures) {
                Write-Output "  - ${package}: Requires WSL Ubuntu to be installed"
            }
            Write-Output ""
            if (-not $isCI) {
                Write-Output "To fix:"
                Write-Output "  1. Install WSL: wsl --install -d Ubuntu"
                Write-Output "  2. Or enable WSL feature: Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux"
                Write-Output "  3. Restart your computer if prompted"
                Write-Output "  4. Run this script again"
                Write-Output ""
            }
            else {
                Write-Output "Note: WSL installation requires elevated privileges or a system restart."
                Write-Output "      In CI environments, ensure WSL is pre-installed or use a runner with WSL support."
                Write-Output ""
            }
        }

        exit 1
    }
}

Write-Output "Installing bwfmetaedit (pinned version)..."

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
                    Write-Output "bwfmetaedit $installedVersion already installed (matches pinned version $version)"
                    $needInstall = $false
                }
                else {
                    Write-Output "Removing existing bwfmetaedit version $installedVersion (installing pinned version $version)..."
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
    }
    catch {
        Write-Output "bwfmetaedit installed but version could not be determined, removing..."
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
        Write-Output "Downloading BWF MetaEdit..."
        New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
        Invoke-WebRequest -Uri $url -OutFile "$tempDir\bwfmetaedit.zip" -UseBasicParsing

        Write-Output "Extracting..."
        Expand-Archive -Path "$tempDir\bwfmetaedit.zip" -DestinationPath $tempDir -Force

        Write-Output "Installing..."
        New-Item -ItemType Directory -Force -Path $installDir | Out-Null
        $exe = Get-ChildItem -Path $tempDir -Filter "bwfmetaedit.exe" -Recurse | Select-Object -First 1
        if (-not $exe) {
            throw "bwfmetaedit.exe not found in downloaded archive"
        }
        Copy-Item -Path $exe.FullName -Destination $exePath -Force

        Write-Output "Adding to PATH..."
        if ($env:GITHUB_PATH) {
            Write-Output "$installDir" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
        }

        Write-Output "Cleanup..."
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Output "bwfmetaedit $version installed successfully"
    }
    catch {
        Write-Error "Failed to install bwfmetaedit: $_"
        exit 1
    }
}

# exiftool: Not needed for e2e tests
# Skip installation on Windows CI since we only run e2e tests
if (-not $isCI) {
    Write-Output "Installing exiftool (pinned version)..."

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
                        Write-Output "exiftool $installedVersion already installed (matches pinned version $exiftoolVersion)"
                        $needInstallExiftool = $false
                    }
                    else {
                        Write-Output "Removing existing exiftool version $installedVersion (installing pinned version $exiftoolVersion)..."
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
        }
        catch {
            Write-Output "exiftool installed but version could not be determined, removing..."
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
        # ExifTool Windows downloads use format: exiftool-VERSION_64.zip
        $url = "https://exiftool.org/exiftool-${exiftoolVersion}_64.zip"
        $tempDir = "$env:TEMP\exiftool"

        try {
            Write-Output "Downloading ExifTool..."
            New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

            # Try downloading the file
            try {
                Invoke-WebRequest -Uri $url -OutFile "$tempDir\exiftool.zip" -UseBasicParsing -ErrorAction Stop
            }
            catch {
                $errorMsg = $_.Exception.Message
                Write-Error "Failed to download exiftool version ${exiftoolVersion}"
                Write-Output "URL attempted: $url"
                Write-Output "Error: $errorMsg"
                Write-Output ""
                Write-Output "The pinned version may not be available for Windows download."
                Write-Output "ExifTool Windows downloads use format: exiftool-VERSION_64.zip"
                Write-Output "Check available versions at: https://exiftool.org/"
                throw "Could not download exiftool version ${exiftoolVersion}. Version may not be available for Windows."
            }

            Write-Output "Extracting..."
            Expand-Archive -Path "$tempDir\exiftool.zip" -DestinationPath $tempDir -Force

            Write-Output "Installing..."
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

            Write-Output "Adding to PATH..."
            if ($env:GITHUB_PATH) {
                Write-Output "$exiftoolInstallDir" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
            }

            Write-Output "Cleanup..."
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Output "exiftool $exiftoolVersion installed successfully"
        }
        catch {
            Write-Error "Failed to install exiftool: $_"
            exit 1
        }
    }
}
else {
    Write-Output "Skipping exiftool installation (not needed for e2e tests on Windows CI)"
}

Write-Output "Verifying installed tools are available in PATH..."

# Refresh PATH to include Chocolatey-installed tools
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Also add manually installed directories to PATH for this session
$manualPaths = @(
    "C:\Program Files\BWFMetaEdit",
    "C:\Program Files\ExifTool",
    "C:\Program Files\id3v2-wrapper"
)

foreach ($path in $manualPaths) {
    if ((Test-Path $path) -and ($env:Path -notlike "*$path*")) {
        $env:Path = "$path;$env:Path"
    }
}

# Refresh PATH in GitHub Actions if available
if ($env:GITHUB_PATH) {
    foreach ($path in $manualPaths) {
        if (Test-Path $path) {
            Write-Output "$path" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append
        }
    }
}

$missingTools = @()
$tools = @("ffprobe", "flac", "metaflac", "mediainfo", "id3v2", "exiftool")

foreach ($tool in $tools) {
    # Skip optional tools in CI (not needed for e2e tests)
    if ($isCI -and ($tool -eq "mediainfo" -or $tool -eq "exiftool")) {
        Write-Output "  ${tool}: Skipped (not needed for e2e tests on Windows CI)"
        continue
    }

    # Skip id3v2 if WSL isn't available (already handled earlier)
    if ($tool -eq "id3v2" -and $wslRequiredPackages -contains "id3v2") {
        Write-Output "  ${tool}: Skipped (WSL not available)"
        continue
    }

    # Check if tool is available
    $toolFound = $false
    $toolPath = Get-Command $tool -ErrorAction SilentlyContinue

    if ($toolPath) {
        $toolFound = $true
        Write-Output "  ${tool}: Found at $($toolPath.Source)"
    }
    else {
        # Check common installation directories
        $commonPaths = @(
            "C:\Program Files\Chocolatey\bin\${tool}.exe",
            "C:\ProgramData\chocolatey\bin\${tool}.exe",
            "C:\Program Files\${tool}\${tool}.exe",
            "C:\Program Files (x86)\${tool}\${tool}.exe"
        )

        foreach ($commonPath in $commonPaths) {
            if (Test-Path $commonPath) {
                $toolFound = $true
                Write-Output "  ${tool}: Found at $commonPath (not in PATH, but installed)"
                # Add to PATH for this session
                $dir = Split-Path -Parent $commonPath
                if ($env:Path -notlike "*$dir*") {
                    $env:Path = "$dir;$env:Path"
                }
                break
            }
        }

        if (-not $toolFound) {
            $missingTools += $tool
            Write-Output "  ${tool}: Not found"
        }
    }
}

if ($missingTools.Count -gt 0) {
    Write-Output ""
    Write-Error "The following tools are not available after installation:"
    foreach ($tool in $missingTools) {
        Write-Output "  - $tool"
    }
    Write-Output ""
    Write-Output "Installation may have failed. Check the output above for errors."
    Write-Output "Note: Some tools may require a new shell session for PATH changes to take effect."
    exit 1
}

# Check if WSL-required packages are missing - warn but don't fail (id3v2 is optional on Windows)
if ($wslRequiredPackages.Count -gt 0) {
    Write-Output ""
    Write-Warning "WSL-required packages could not be installed:"
    Write-Output "  $($wslRequiredPackages -join ', ')"
    Write-Output ""
    if ($isCI) {
        Write-Output "These packages require WSL Ubuntu which is not available in this CI environment."
        Write-Output "Tests requiring these tools will be skipped on Windows."
        Write-Output ""
        Write-Output "To enable these tools in CI:"
        Write-Output "  1. Use a Windows runner with WSL pre-installed"
        Write-Output "  2. Or configure WSL in your CI workflow before running this script"
    }
    else {
        Write-Output "These packages require WSL Ubuntu to be installed."
        Write-Output ""
        Write-Output "To fix:"
        Write-Output "  1. Install WSL: wsl --install -d Ubuntu"
        Write-Output "  2. Or enable WSL feature: Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux"
        Write-Output "  3. Restart your computer if prompted"
        Write-Output "  4. Run this script again"
    }
    Write-Output ""
}
else {
    Write-Output "All system dependencies installed successfully!"
}




