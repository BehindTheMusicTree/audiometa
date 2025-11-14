#!/bin/bash
# Wrapper for PowerShell ScriptAnalyzer that skips on macOS if PowerShell isn't available

# Check if PowerShell is available
if ! command -v pwsh &>/dev/null; then
  # On macOS, PowerShell might not be installed - skip linting
  if [[ "$OSTYPE" == "darwin"* ]]; then
    exit 0
  fi
  # On other systems, fail if PowerShell is required but not found
  echo "ERROR: PowerShell (pwsh) is required but not found."
  echo "Install PowerShell Core: https://github.com/PowerShell/PowerShell#get-powershell"
  exit 1
fi

# Run PowerShell ScriptAnalyzer for each file
# This replicates the behavior of the py-psscriptanalyzer hook
for file in "$@"; do
  pwsh -Command "
    if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
      Write-Host 'PSScriptAnalyzer module not found. Installing...' -ForegroundColor Yellow
      Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force -SkipPublisherCheck
    }
    Import-Module PSScriptAnalyzer
    \$results = Invoke-ScriptAnalyzer -Path \"$file\" -Severity Error,Warning
    if (\$results) {
      \$results | ForEach-Object {
        Write-Host \"\$(\$_.ScriptName):\$(\$_.Line): \$(\$_.Message)\" -ForegroundColor Red
      }
      exit 1
    }
  " || exit 1
done

