#!/bin/bash
# Wrapper for PowerShell ScriptAnalyzer
# Requires PowerShell Core (pwsh) to be installed

# Check if PowerShell is available
if ! command -v pwsh &>/dev/null; then
  echo "ERROR: PowerShell (pwsh) is required but not found."
  echo ""
  echo "Install PowerShell Core:"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  macOS: brew install --cask powershell"
    echo "  Or download from: https://github.com/PowerShell/PowerShell#get-powershell"
  else
    echo "  Visit: https://github.com/PowerShell/PowerShell#get-powershell"
  fi
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
