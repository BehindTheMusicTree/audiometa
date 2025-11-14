#!/bin/bash
# Wrapper for PowerShell ScriptAnalyzer format check that skips on macOS if PowerShell isn't available

# Check if PowerShell is available
if ! command -v pwsh &>/dev/null; then
  # On macOS, PowerShell might not be installed - skip formatting check
  if [[ "$OSTYPE" == "darwin"* ]]; then
    exit 0
  fi
  # On other systems, fail if PowerShell is required but not found
  echo "ERROR: PowerShell (pwsh) is required but not found."
  echo "Install PowerShell Core: https://github.com/PowerShell/PowerShell#get-powershell"
  exit 1
fi

# Run PowerShell ScriptAnalyzer format check for each file
# This replicates the behavior of the py-psscriptanalyzer-format hook
for file in "$@"; do
  pwsh -Command "
    if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
      Write-Host 'PSScriptAnalyzer module not found. Installing...' -ForegroundColor Yellow
      Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force -SkipPublisherCheck
    }
    Import-Module PSScriptAnalyzer
    \$content = Get-Content \"$file\" -Raw
    \$formatted = \$content | Invoke-Formatter
    if (\$content -ne \$formatted) {
      Write-Host \"File needs formatting: $file\" -ForegroundColor Yellow
      exit 1
    }
  " || exit 1
done

