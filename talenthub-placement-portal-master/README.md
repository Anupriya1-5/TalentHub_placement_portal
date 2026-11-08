# TalentHub Campus Placement Management System (v2)

TalentHub is a full-stack web application that manages the college placement process end-to-end:
students apply for jobs, companies shortlist eligible students, interviews get scheduled and
recorded, offers are issued and accepted, and the placement coordinator tracks placement statistics.

Built with a layered architecture:

```
backend/
  app/
    api/          # Router layer (FastAPI routers)
    core/         # Database config, JWT auth / security
    models/       # SQLAlchemy models (Student, Company, JobListing, Application, Interview, Offer, User)
    repositories/ # Data-access layer
    services/     # Business logic (eligibility rules, placement workflow, auth)
    schemas/      # Pydantic request/response schemas
  main.py         # FastAPI entry point (seeds demo data on first run)
  requirements.txt
frontend/
  src/
    pages/        # Login, StudentDashboard, CompanyDashboard, CoordinatorDashboard
    components/    # Header, StatusBadge
    api.js         # Axios client with JWT auth
  package.json
```

---

## Step-by-step: how to run it locally

### 1. Prerequisites

- **Python 3.9+** installed and added to PATH (tested on Python 3.13).
- **Node.js v18+** and npm installed.
- A terminal — PowerShell / Command Prompt on Windows, or any shell on macOS/Linux.

### 2. Get the code

```bash
git clone https://github.com/kachavimathamit/talenthub-placement-portal.git
cd talenthub-placement-portal
```

(Or download/extract the project into a folder of your choice — the paths below assume
`D:\Gemini\Talenthub v2`; adjust to wherever you placed it.)

### 3. Start the backend (Terminal window 1)

```bash
cd "D:\Gemini\Talenthub v2\backend"

# Create a virtual environment
python -m venv venv

# Activate it
# Windows PowerShell:
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

- On first run the server automatically creates `talenthub.db` (SQLite) and seeds it with demo
  students, companies, job listings and login accounts — no manual setup needed.
- **Backend verification:** open http://127.0.0.1:8000/docs to see the interactive Swagger API docs,
  or http://127.0.0.1:8000/ for a welcome message.

### 4. Start the frontend (Terminal window 2 — leave the backend running)

```bash
cd "D:\Gemini\Talenthub v2\frontend"

# Install npm packages
npm install

# Start the Vite dev server
npm run dev
```

- **Frontend access:** open http://localhost:5173 in your browser.

### 5. Log in and try it out

On the login screen, click any of the demo-account buttons to auto-fill the email (password is
always `password123`), then click **Sign In**. See the [Demo accounts](#demo-accounts-seeded-automatically-on-first-backend-start)
table below for the full list, and [Suggested walkthrough](#suggested-walkthrough) for a guided
tour of the whole placement flow.

### 6. Common troubleshooting

| Problem | Fix |
|---|---|
| PowerShell blocks `venv\Scripts\activate` with an execution-policy error | Run PowerShell as Administrator, or run `Set-ExecutionPolicy Unrestricted -Scope Process` in the current window, then retry. |
| `Port 8000 already in use` | Another process is using it — stop it, or run uvicorn on a different port (`--port 8001`) and update `baseURL` in `frontend/src/api.js` to match. |
| `Port 5173 already in use` | Vite will usually auto-pick the next free port (e.g. 5174) — check the terminal output for the actual URL. |
| `ModuleNotFoundError: greenlet` or similar import errors | Re-run `pip install -r requirements.txt` inside the activated venv. |
| Frontend shows network/CORS errors | Make sure the backend is running on port 8000 first — the frontend always calls `http://127.0.0.1:8000`. |
| `node_modules` missing / npm errors | Delete `frontend/node_modules` and run `npm install` again. |
| Want a clean slate / reset all demo data | Stop the backend, delete `backend/talenthub.db`, and restart uvicorn — it reseeds automatically. |

---

## Demo accounts (seeded automatically on first backend start)

All demo accounts use the password `password123`.

| Role        | Email                          |
|-------------|---------------------------------|
| Student     | rahul@student.talenthub.edu     |
| Student     | priya@student.talenthub.edu     |
| Student     | aman@student.talenthub.edu      |
| Company (HR)| hr@abctech.com                  |
| Company (HR)| hr@xyzcorp.com                  |
| Coordinator | coordinator@talenthub.edu       |

## Suggested walkthrough

1. **Sign in as a Student** (e.g. `rahul@student.talenthub.edu`) — view job listings (eligibility
   is checked live against CGPA / backlog criteria) and apply to one you're eligible for.
2. **Log out, sign in as a Company** (e.g. `hr@abctech.com`) — optionally post a new job listing,
   then open **Applicants**, shortlist the student, pick an interview date/time and schedule it.
3. Still as the company, mark the interview result **Pass**, enter a package (LPA) and **Issue Offer**.
4. **Log out, sign back in as the same Student** — see the offer under "My Applications" and
   **Accept** (or Decline) it.
5. **Log out, sign in as the Coordinator** (`coordinator@talenthub.edu`) — view placement
   statistics (total students, companies, active drives, offers issued, placement %) and the full
   table of all applications across the system.

## Workflow summary

1. **Student** logs in, views eligible job listings, and applies.
2. **Company** logs in, posts job listings, views applicants, shortlists/rejects, schedules
   interviews, records pass/fail results, and issues offers to students who passed.
3. **Student** accepts or declines the offer.
4. **Coordinator** logs in to view placement statistics and a full table of all applications
   across the system.

---

## TalentHub 2.0 enhancements

This version adds five connected career-support features while retaining the original layered FastAPI + React architecture.

### 1. Resume Analyzer
- Student uploads a text-based PDF resume (maximum 5 MB).
- The backend extracts text with `pypdf` and detects a curated set of technical and professional skills.
- The detected skill list is saved against the authenticated student account. The raw resume text/file is not stored.
- Scanned/image-only PDFs are not OCR processed; upload a selectable-text PDF.

### 2. Smart Job Matching
- Compares detected resume skills with skills mentioned in each job title and description.
- Displays a transparent skill-overlap percentage, matched skills, missing skills, and academic eligibility.
- This is a keyword-based recommendation aid, not an AI hiring decision.

### 3. Skill Gap Analysis
- Students can open a job's skill gap to see skills detected in their resume versus skills mentioned in that job description.
- Recommendations are based only on the wording of the job listing and should be reviewed by the student.

### 4. Placement Analytics
- Coordinator dashboard includes application-status and company-wise application breakdowns, interview count, job count, and placement percentage.
- Charts are rendered using lightweight CSS bars; no extra chart library is required.

### 5. Interview Scheduler
- Company dashboard retains its existing schedule/result controls and now includes a consolidated interview calendar.
- Student dashboard shows their scheduled interviews; coordinator access can view all scheduled interviews through the API.

### New API endpoints
- `POST /students/me/resume` — upload and analyze a PDF resume (Student)
- `GET /students/me/skills` — retrieve saved skills (Student)
- `GET /students/me/recommendations` — ranked job matches (Student)
- `GET /students/me/skill-gap/{job_id}` — skill gap for a job (Student)
- `GET /coordinator/analytics` — placement analytics (Coordinator)
- `GET /interviews/calendar` — role-scoped interview calendar (Student, Company, Coordinator)

### Run the enhanced version
Backend setup is unchanged except that `pip install -r requirements.txt` now installs `pypdf` for PDF text extraction. If you already have a virtual environment, run the install command again after replacing the project files.

```powershell
# Terminal 1
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

# Terminal 2
cd frontend
npm.cmd install
npm.cmd run dev
```

The SQLite database automatically creates the new skill-profile table on startup. Existing student, company, and application records are retained.
