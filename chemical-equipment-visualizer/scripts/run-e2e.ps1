# Run E2E smoke checks using the project's venv Python
# Usage: .\scripts\run-e2e.ps1
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $repoRoot '..\.venv\Scripts\python.exe'
if (-Not (Test-Path $py)) { Write-Error "Python not found at $py - activate your venv or adjust the script"; exit 1 }

& $py "..\backend\scripts\check_endpoints.py" | Write-Host

Write-Host "E2E script finished; check backend/docs for generated report and artifacts."