# Release artifacts and running packaged desktop app

This repo's GitHub Actions CI packages a Windows desktop artifact using PyInstaller and uploads it as an artifact named `ChemicalVisualizer-windows`.

## Where to find release artifacts
- In the GitHub Actions run for a successful build, go to the `Artifacts` area and download `ChemicalVisualizer-windows`.

## Run the packaged app (Windows)
- Double-click `ChemicalVisualizer.exe` or run from PowerShell/Command Prompt:
  .\ChemicalVisualizer.exe

## Headless / CI mode: perform an upload via the packaged EXE
The desktop EXE supports a simple headless mode useful for CI or automation:

--upload-ci --csv <path-to-csv> --token <api-token> [--api <base-api-url>]

Example (PowerShell):

.\ChemicalVisualizer.exe --upload-ci --csv C:\path\to\sample_upload.csv --token b9edaf7c... --api http://127.0.0.1:8000/api

The exit codes:
- 0: upload succeeded and rows were created
- 2: upload failed (non-200 or no rows created)
- 3: request or file error

This mode is used by CI to verify the packaged EXE can perform a basic upload against a local backend.
