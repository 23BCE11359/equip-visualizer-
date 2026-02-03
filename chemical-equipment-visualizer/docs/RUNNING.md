# How to run this project (quick guide)

## Prerequisites
- Windows (tested) or Linux/Mac with equivalents
- Python 3.11+ and Node 18+
- A virtualenv (recommended) at `.venv` at repo root

## One-time setup
1. Create and activate venv (recommended):
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # PowerShell

2. Install backend deps:
   python -m pip install --upgrade pip
   python -m pip install -r backend/requirements.txt

3. Install frontend deps:
   cd frontend-web
   npm install

4. (Optional) Install desktop build deps:
   cd frontend-desktop
   python -m pip install -r requirements.txt

## Start dev servers (fast)
Option A (manual):
- Backend: cd backend && python manage.py migrate && python manage.py runserver 0.0.0.0:8000
- Frontend: cd frontend-web && npm run dev (open http://127.0.0.1:5173)

Option B (helper script):
- From repo root run: `.\iles\scripts\start-dev.ps1` (this opens two PowerShell windows, one for backend and one for frontend)

## Quick demo (E2E smoke)
1. Create demo user (if not already):
   cd backend
   python manage.py create_demo_user

2. Run E2E helper (from repo root):
   .\scripts\run-e2e.ps1

Check results:
- PDF report saved at `backend/docs/e2e_report_<id>.pdf`
- Desktop executable (if packaged) at `backend/docs/artifacts/ChemicalVisualizer.exe`

## Packaging desktop app (Windows)
From `frontend-desktop/`:
- python -m pip install -r requirements.txt
- python -m PyInstaller --onefile --name ChemicalVisualizer main.py
- Built exe: `frontend-desktop/dist/ChemicalVisualizer.exe`

### Headless / automation mode
The packaged exe supports a headless action useful for CI automation to upload a CSV directly:

Example:

```
frontend-desktop\dist\ChemicalVisualizer.exe --upload-ci --csv frontend-desktop\test_data\sample_upload.csv --token <token> --api http://127.0.0.1:8000/api
```

Exit codes:
- 0: upload succeeded
- 2: upload failed or no rows created
- 3: error (file, request, etc.)

## Notes & troubleshooting
- If frontend fails to start, run `npm install --legacy-peer-deps` and retry.
- If PDF endpoint returns 501, ensure `reportlab` is installed in backend env.
- Use `python manage.py create_demo_user` to get demo credentials (`demo/demo`) and token printed to console.
- Desktop: If upload or report download fails with a connection error, use the **Set API URL** button in the app to point it at the backend (e.g. `http://127.0.0.1:8000/api`). The app shows connection status in the top bar and provides Retry / Set API URL / Open docs options if it cannot reach the server. You can change the theme (Warm / Neutral) and adjust font size (A+/A-) in the top-right header. The setting is persisted to your home directory in `.chemical_visualizer_config.json`.

- Releases: Tag a Git reference (e.g., `v1.0.0`) to trigger an automated Windows release build which will attach the packaged `ChemicalVisualizer.exe` to the GitHub Release. See `docs/RELEASE.md` for details.

---
If you want, I can now run the helper script and do a short live walkthrough showing each step and explaining what each command does. Say "Start walkthrough" and I will proceed.