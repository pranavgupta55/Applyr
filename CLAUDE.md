# Applyr Project Guidelines

I need you to generate a COMPLETE, ROBUST, and PRODUCTION-READY internship application bot. This is a "Human-in-the-Loop" automation system. It runs LOCALLY on a Mac M4.

**CORE PHILOSOPHY:**
1. **No Frontend Frameworks:** Do NOT use React, Next.js, or TypeScript. Use **Streamlit** for the UI. It is Python-only and robust.
2. **Local First:** Storage is **SQLite**. No Supabase.
3. **Speed:** The backend is **FastAPI** (Uvicorn). The frontend connects via API calls.
4. **Human Verification:** The bot automates the boring stuff (finding, parsing, drafting), but I (the user) press the final "Apply" and "Send Email" buttons.

---

### **1. DATA & CONTEXT (Pre-Populated)**

You must create a `data/profile.json` based on the following OCR text from my actual Resume. Use this to populate skills, education, and experience bullets.

**My Resume Data:**
Name: Pranav Gupta
Email: pranavgupta5581@gmail.com / pranav@seas.upenn.edu
Links: linkedin.com/in/pgupta55, github.com/pranavgupta55
Education: UPenn (Robotics MSE, AI BSE, May 2029/2026), UT Dallas (HS, GPA 4.58).
Skills: Python, C++, OCaml, React, FastAPI, PyTorch, ROS, Computer Vision, Fusion 360.
Experience:
1. Autonomous Driving Research Intern (UT Dallas): Published paper, reduced training time 36h->24h, Keras/TensorFlow.
2. Co-Founder Solar Car Team: Raised $6.5k, Fusion 360 chassis design, 4th nationally.
Projects: Recall AI (FastAPI/GPT-4o), Python Coding Projects (100+ projects, PPO RL drone control).

**Cover Letter Strategy:**
I use a "Modular" approach.
- **Static Content:** Header, Intro, Body Paragraph 1 (Technical - SpaceX/Research example), Body Paragraph 2 (Soft Skills - Solar Car example), Sign-off.
- **Dynamic Content:** The "Why This Company" paragraph. This is the ONLY part the LLM generates based on the Job Description.
- **Output:** A PDF generated via Python (`reportlab`) that mimics the formatting of a standard Google Doc (Times New Roman, 11pt).

---

### **2. ARCHITECTURE**

**Stack:** Python 3.11+, FastAPI, Streamlit, SQLite, Playwright, OpenAI API.

**Directory Structure:**
intern-bot/
├── backend/
│ ├── main.py # FastAPI Router
│ ├── scraper.py # GitHub (Simplify/Speedy) + Handshake/Direct URL logic
│ ├── analyzer.py # LLM: Tagging, Resume Selection, Cover Letter Gen
│ ├── pdf_engine.py # ReportLab PDF generation (pixel-perfect formatting)
│ ├── email_engine.py # DNS/SMTP checks + Email pattern generation
│ ├── db.py # SQLite ORM (using sqlite-utils or raw SQL)
│ └── models.py # Pydantic models
├── frontend/
│ ├── app.py # Streamlit Dashboard
│ ├── components.py # Reusable UI bits (Kanban columns, etc.)
│ └── utils.py # API helpers
├── data/
│ ├── jobs.db # Main Database
│ ├── profile.json # My Profile Data
│ ├── answers.json # Bank of common behavioral answers
│ └── resumes/ # Folder containing PDFs: "resume_cv.pdf", "resume_backend.pdf", "resume_general.pdf"
├── templates/
│ └── cover_letter.txt # Jinja2 template for the text content
└── requirements.txt
code
Code
---

### **3. DETAILED COMPONENT LOGIC**

#### **A. Database Schema (`jobs.db`)**
- **Table `jobs`:** `id`, `company`, `role`, `link` (application URL), `origin` (GitHub/Manual), `status` (New, Analyzed, Applied, Rejected), `priority_score` (int), `tags` (JSON), `notes`, `date_found`, `deadline`.
- **Table `companies`:** `id`, `name`, `domain`, `penn_connection` (bool - flag if UPenn alumni/partners found), `email_pattern` (e.g., "{first}.{last}").
- **Table `contacts`:** `id`, `company_id`, `name`, `role`, `email`, `email_status` (Verified/Guessed), `outreach_status` (Drafted, Sent).

#### **B. The "Sync" Pipeline (`scraper.py`)**
- **GitHub Source:** Scrape `SimplifyJobs/Summer2026-Internships` and `speedyapply` READMEs. Extract Company, Role, Link.
- **Manual Source:** API endpoint to accept a URL (Handshake or Company Page).
- **Enrichment:**
    1. If it's a direct company link, use **Playwright** to extract the page text.
    2. Check for "University of Pennsylvania" or "UPenn" in text to set `penn_connection=True`.

#### **C. The "Brain" (`analyzer.py`)**
- Use OpenAI (`gpt-4o-mini`).
- **Input:** Job Description text.
- **Output (JSON):**
    - `tags`: e.g., ["Computer Vision", "Backend", "Robotics"].
    - `resume_match`: "resume_cv.pdf" vs "resume_backend.pdf" (based on tags).
    - `priority`: High/Med/Low (Logic: High if "Google/SpaceX" OR deadline < 7 days OR Penn connection).
    - `why_us_paragraph`: A 3-4 sentence paragraph tailored to the company values found in text.

#### **D. The PDF Factory (`pdf_engine.py`)**
- Use `reportlab`.
- **Layout:** Replicate standard letter format.
- **Logic:**
    1. Load `profile.json` (Header info).
    2. Load `data/resumes/{selected_resume}` (to know context, though we just upload the file).
    3. Construct the Cover Letter:
       [Header] -> [Static Intro] -> [Static Project Paragraphs] -> [**Dynamic Why Us**] -> [Sign off].
    4. Save as `temp/Cover_Letter_{Company}.pdf`.

#### **E. Email & Contact Discovery (`email_engine.py`)**
- **Domain Discovery:** Search Google (via `googlesearch-python`) if domain missing.
- **Pattern Logic:** Try 10 common formats ({f}.{last}, {first}{last}, etc.).
- **Verification:**
    1. **Syntax Check**: Regex.
    2. **DNS Check**: `dnspython` for MX records.
    3. **Safe SMTP**: Attempt connection. If catch-all or block, mark "Risky". If 250 OK, mark "Verified".
    4. **Rate Limit**: Max 1 SMTP check per 2 seconds.

#### **F. Frontend UI (`frontend/app.py`)**
- **Dashboard (Kanban Style):**
    - Columns: **New Jobs** (Sync Button here), **Analysis Ready** (AI Done), **Applied**.
    - Rows: Each job card shows Priority ID, Tags, Company.
- **Action Mode (The "Apply" Flow):**
    - Click a Job -> Opens Side Panel.
    - Shows: "Resume Strategy: CV Focus" (Dropdown to override).
    - Shows: Generated "Why Us" paragraph (Editable text area).
    - **Button: "Generate Assets"**: Creates the PDF locally.
    - **Button: "Launch Application"**:
        1. Copies "Why Us" text to clipboard.
        2. Opens Application URL in Browser.
        3. Opens `data/resumes/` folder in Finder (so I can drag-drop).
- **Cold Email Tab:**
    - Input: Company Domain.
    - Action: "Find Contacts" (Scrapes LinkedIn "People" page logic - *simulated via search link*).
    - Action: "Generate Draft".
- **Calendar View:** Simple timeline of when jobs were found vs deadlines.

---

### **4. IMPLEMENTATION INSTRUCTIONS**

1. **Environment:** Use `python-dotenv` for API keys.
2. **Raycast Integration:** Explain how to set up the Raycast snippets (`cmd+1` for name, etc.) in the README, don't write code for it (it's external).
3. **Dependencies:** `fastapi`, `uvicorn`, `streamlit`, `playwright`, `openai`, `reportlab`, `sqlite-utils`, `beautifulsoup4`, `googlesearch-python`, `pandas`.

**GENERATE THE COMPLETE PROJECT CODE.**
Start with `requirements.txt`, then the database setup, backend logic, and finally the Streamlit frontend. Ensure no placeholders exist—write the actual prompt engineering logic for the AI analyzer.