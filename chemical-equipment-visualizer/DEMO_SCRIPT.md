# Chemical Equipment Visualizer — 3-Minute Demo Script

## Overview
Demonstrate a complete workflow: upload CSV → explore data → filter → export → generate PDF report.

---

## Scene 1: Introduction (0:00–0:30)
**Narration:** "Welcome to the Chemical Equipment Visualizer. This tool helps you upload, analyze, and report on chemical equipment data with ease. Let me walk you through a quick demo."

**On Screen:**
- Show the home page with the header "Chemical Equipment Visualizer"
- Highlight the three main buttons: Upload CSV, Export CSV, and Demo Data
- Briefly show the onboarding card explaining the 3 main features

---

## Scene 2: Upload CSV (0:30–1:00)
**Narration:** "First, let's upload a sample equipment dataset."

**Actions:**
1. Click "Upload CSV" button
2. Select `frontend-desktop/test_data/sample_upload.csv` or similar
3. Wait for upload to complete and show success notification
4. Show the table populating with equipment records (e.g., pumps, compressors, heat exchangers)

**On Screen:**
- Display file selection dialog
- Show success toast notification
- Display the uploaded dataset in the equipment table with columns: Name, Type, Pressure Rating, Temperature Rating, etc.

---

## Scene 3: Explore with Charts (1:00–1:45)
**Narration:** "The app automatically generates summary statistics and charts so you can quickly understand your data."

**Actions:**
1. Scroll down to show the **Summary Cards** (Total Equipment, Average Pressure, Average Temperature, Type Distribution)
2. Click on and briefly highlight each chart:
   - **Equipment Type Distribution** (pie/bar chart)
   - **Pressure vs Temperature** (scatter plot)
   - **Equipment by Category** (bar chart)
3. Show the **History section** displaying previously uploaded datasets

**On Screen:**
- Emphasize the summary numbers and visual charts
- Highlight how quickly insights are available without writing code

---

## Scene 4: Filter & Export (1:45–2:30)
**Narration:** "You can filter the data by equipment type, pressure, and temperature range, then export the filtered results."

**Actions:**
1. Show the filter sidebar (if available) or filter options
2. Apply a filter (e.g., Type = "Pump", Pressure > 50)
3. Show the table filtering in real-time
4. Click "Export CSV" button
5. Show file saving notification (or downloaded file)

**On Screen:**
- Demonstrate responsive filtering UI
- Show the CSV export in action
- Emphasize the simplicity of exporting custom datasets

---

## Scene 5: Generate PDF Report (2:30–3:00)
**Narration:** "Finally, let's generate a professional PDF report of our dataset. This includes a summary, charts, and equipment details — all in one document."

**Actions:**
1. Click on an uploaded dataset in the History section
2. Click "Download Report" or navigate to API report endpoint
3. Show the PDF downloading or opening
4. Briefly display the PDF (cover page showing title, summary stats, and first page of charts)

**On Screen:**
- Show the PDF report icon and download action
- Display the generated PDF with title, summary, and charts
- Emphasize the professional formatting

---

## Scene 6: Closing (Optional)
**Narration:** "That's the Chemical Equipment Visualizer. Upload CSV files, explore your equipment with interactive charts, filter and export data, and generate professional reports — all in one friendly and intuitive interface."

**On Screen:**
- Return to home page
- Show all three frontend options: Web (browser), Desktop (PyQt5), and API
- Display GitHub repo link or project information

---

## Technical Notes for Filming

### Pre-Demo Setup
- Have a clean browser (no extensions interfering)
- Pre-load sample CSV data in `frontend-desktop/test_data/sample_upload.csv`
- Run backend: `cd backend && python manage.py migrate && python manage.py runserver 0.0.0.0:8000`
- Run frontend: `cd frontend-web && npm run dev` (opens http://127.0.0.1:5173)
- Optionally create demo user: `python manage.py create_demo_user`

### Recording Tips
- Use 1920×1080 resolution
- Zoom cursor for better visibility
- Slow down clicks (500ms pause before and after)
- Use screen capture tool: OBS Studio, Camtasia, or ScreenFlow
- Record audio separately and sync in post-production for better quality
- Total runtime: ~3 minutes at normal speed

### Audio Notes
- Speak clearly and at a moderate pace
- Include 1–2 second pauses between scenes for visual impact
- Optional: add subtle background music (royalty-free)

---

## Timing Breakdown
| Section | Duration |
|---------|----------|
| Intro | 30 sec |
| Upload | 30 sec |
| Charts | 45 sec |
| Filter & Export | 45 sec |
| PDF Report | 30 sec |
| **Total** | **3 min** |

---

## Alternative: Desktop App Demo
If demoing the **desktop app** instead, the flow is similar:
1. **Launch** the PyQt5 app
2. **Set API URL** to `http://127.0.0.1:8000/api` if needed
3. **Upload CSV** via file dialog
4. **View Matplotlib charts** (pressure vs temperature, equipment distribution)
5. **Export CSV** from the desktop interface
6. **Generate/Download PDF report**

---

## Live Demo Walkthrough (Interactive)
If presenting live, you can pause and ask the audience:
- "What equipment type would you like to filter by?" (interact with filters)
- "Would you like to see the desktop or web version?" (show flexibility)
- "Should we export or generate a report?" (give them choice)

This adds engagement and makes the demo memorable.
