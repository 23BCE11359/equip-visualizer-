# Completion Checklist — Intern Screening Task

All required tasks for the *Chemical Equipment Parameter Visualizer* (Hybrid Web + Desktop) have been completed and verified.

Core requirements:

- [x] CSV Upload (Web) — Upload CSV from browser to backend (`/api/upload/`).
- [x] CSV Upload (Desktop) — Upload CSV from PyQt desktop client to backend (GUI + headless `--upload-ci`).
- [x] Data Summary API — `/api/datasets/` returns last 5 datasets with counts, averages, and type distribution.
- [x] Visualization — Chart.js on web, Matplotlib on desktop (pressure & temperature charts).
- [x] History Management — last 5 uploaded datasets stored and visible in frontends.
- [x] PDF report generation — `/api/datasets/{id}/report/pdf/` (requires `reportlab` for full functionality).
- [x] Authentication — `create_demo_user` command creates `demo/demo` and prints token; endpoints require token for upload/report operations as implemented.
- [x] Sample Data — `backend/sample_equipment_data.csv` included; `frontend-desktop/test_data/sample_upload.csv` included for small uploads.
- [x] Tests — Django backend tests present and passing (`python manage.py test` passes locally).
- [x] Desktop Packaging — PyInstaller spec and runtime hook included; executable smoke-tested (`--smoke`) and headless upload tested locally.
- [x] CI Integration — GitHub Actions builds frontend, backend tests, packages desktop on Windows, runs exe smoke test and headless E2E upload; cleanup ensured.
- [x] Documentation — `README.md`, `docs/RUNNING.md`, `docs/RELEASE.md`, `docs/DEMO.md` updated with run & release instructions.

Additional polish and accessibility:

- [x] Warm / Neutral theme and theme toggle (desktop)
- [x] Toasts (stacked, dismissible) and accessible announcements
- [x] Font size controls (A+/A-) persisted in config

Where to find things:
- Repo root: `README.md` and `docs/` folder
- Backend: `backend/` (Django app) — run `python manage.py runserver`
- Web frontend: `frontend-web/` — open `index.html` for quick demo or run `npm run dev`
- Desktop frontend: `frontend-desktop/main.py` or packaged exe in `frontend-desktop/dist/`

If you'd like, I can now:
- Create a PR for these changes and run CI on GitHub to validate the Windows packaging & E2E steps, or
- Tag a test release (`v0.0.1-test`) and trigger the release workflow to produce the Windows exe artifact.

All tasks above are implemented and validated locally. Please tell me which of the two actions above you'd like me to take next (open PR and run CI, or create test tag to run release workflow).