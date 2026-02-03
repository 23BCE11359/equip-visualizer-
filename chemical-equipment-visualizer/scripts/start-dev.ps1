# Start backend and frontend dev servers in new PowerShell windows
# Usage: Open an elevated PowerShell at repo root then run: .\scripts\start-dev.ps1

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Path to virtualenv python (adjust if your venv is elsewhere)
$venvPython = Join-Path $repoRoot '..\.venv\Scripts\python.exe'
if (-Not (Test-Path $venvPython)) {
    Write-Host "Warning: venv python not found at $venvPython. Make sure your venv is created and activated."
}

# Start backend
$backendCmd = "cd `"$repoRoot\..\backend`"; & `"$venvPython`" manage.py runserver 0.0.0.0:8000"
Start-Process -FilePath pwsh -ArgumentList "-NoExit","-Command",$backendCmd -WindowStyle Normal
Write-Host "Started backend in a new PowerShell window (http://127.0.0.1:8000/)"

# Start frontend (Vite)
$frontendCmd = "cd `"$repoRoot\..\frontend-web`"; npm run dev"
Start-Process -FilePath pwsh -ArgumentList "-NoExit","-Command",$frontendCmd -WindowStyle Normal
Write-Host "Started frontend dev server in a new PowerShell window (http://127.0.0.1:5173/)"

Write-Host "If any window reports missing dependencies, cd into the respective folder and run the install commands listed in README."