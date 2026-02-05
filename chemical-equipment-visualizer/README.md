# Chemical Equipment Parameter Visualizer (Hybrid)

This repository contains a Django REST backend and two frontends:

- Web frontend (React + Chart.js — uses a small in-browser React app) in `frontend-web/`
- Desktop frontend (PyQt5 + Matplotlib) in `frontend-desktop/`

## Features
- CSV upload (backend parses CSV with pandas)
- Summary API (counts, averages, type distribution)
- Charts (Chart.js on web, Matplotlib on desktop)
- History (last 5 uploaded datasets)
- CSV export of filtered data
- PDF report generation endpoint (requires `reportlab`)
- Token-based auth available: POST `/api-token-auth/` returns an API token for username/password (use the token in `Authorization: Token <token>` header for dataset report downloads)
- Upload endpoint now requires authentication: `POST /api/upload/` (use token header when uploading CSV from web or desktop clients).  
- Management command: `python manage.py load_sample` — loads `backend/sample_equipment_data.csv` into the database for demo purposes.
- Management command: `python manage.py create_demo_user` — creates a demo user (`demo/demo`) and prints an API token.
- Management command: `python manage.py generate_report --dataset <id> --out <path>` — generate a PDF report file for a dataset.
- Basic authentication support (DRF Basic + Session)

## Quick start (backend)

1. Create and activate a Python virtualenv (recommended):

   python -m venv venv
   venv\Scripts\activate

2. Install required packages:

   pip install django djangorestframework django-filter pandas djangorestframework-csv

   Optional (for PDF generation):

   pip install reportlab

3. Run migrations and create superuser:

   cd backend
   python manage.py migrate
   python manage.py createsuperuser

4. Run development server:

   python manage.py runserver

   - API root available at: http://127.0.0.1:8000/api/
   - Upload endpoint: POST http://127.0.0.1:8000/api/upload/ (multipart form-data with `file`)
   - Datasets list: GET http://127.0.0.1:8000/api/datasets/
   - Dataset PDF: GET http://127.0.0.1:8000/api/datasets/{id}/report/pdf/ (requires authentication)

## Web frontend

This repository includes a lightweight React app scaffold (Vite) in `frontend-web/`.

Development (fast):

1. cd frontend-web
2. npm ci
3. npm run dev

Production build:

1. cd frontend-web
2. npm ci
3. npm run build

The dev server runs on `http://localhost:5173` by default; the app communicates with the backend at `http://127.0.0.1:8000/`.

Note: The previous in-browser demo remains available as `index.html` for quick previews but the recommended workflow is the Vite app.

## Desktop frontend

Run the PyQt5 app (development):

   pip install pyqt5 matplotlib requests
   python frontend-desktop/main.py

Package a Windows executable (PyInstaller):

1. Activate your virtualenv and from the `frontend-desktop/` directory run:

   python -m pip install -r requirements.txt
   python -m PyInstaller --onefile --name ChemicalVisualizer main.py

2. The built exe will be in `frontend-desktop/dist/ChemicalVisualizer.exe`. You can run it directly on Windows to start the desktop app.

Note: The packaged exe is a single-file binary — include the documentation and licenses when distributing.


## Tests

Run Django tests (backend):

   cd backend
   python manage.py test

## Artifacts & sample outputs

- Built Windows executable (packaged desktop app): `backend/docs/artifacts/ChemicalVisualizer.exe` (created locally or produced by CI).  
- Sample E2E PDF report generated during verification: `backend/docs/e2e_report_4.pdf`.


## Notes & Next steps
- The web UI is implemented as an in-browser React app (for simple demo purposes). For production, convert to a proper React app build (CRA/Vite) and add CORS/auth handling.
- PDF report generation requires `reportlab` — without it the endpoint returns 501.
- Authentication is provided by DRF Basic and Session; for scripted or desktop auth flows consider adding token-based auth.

