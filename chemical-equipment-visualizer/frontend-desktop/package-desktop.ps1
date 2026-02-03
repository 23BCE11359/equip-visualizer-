# PowerShell script to build desktop executable using PyInstaller
# Usage: Open an elevated PowerShell with activated venv and run: .\package-desktop.ps1

python -m pip install -r requirements.txt
pyinstaller --onefile --name ChemicalVisualizer main.py

Write-Host "Executable should be in the dist\ folder"