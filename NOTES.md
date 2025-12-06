### **GLOBAL CONTEXT & SYSTEM DEFINITION**

**1. The Core Objective**
You are building a "Human-in-the-Loop" Internship Application Bot. The goal is **speed** and **reliability**, not total automation. The system automates the tedious "prep work" (finding jobs, parsing requirements, generating tailored cover letters, drafting emails) but leaves the final execution (form submission, email sending) to the human user to prevent errors and bans.

**2. Hardware & Environment Constraints**
*   **Machine:** Mac M4 (Apple Silicon).
*   **Deployment:** Localhost ONLY. No Docker. No Cloud (AWS/GCP). No remote servers.
*   **OS Integration:** The system must play nicely with macOS features (Finder, Clipboard).
*   **Run Mode:** The system does **not** run as a hidden background daemon. It runs on-demand via a "Sync" button triggered by the user in the UI.

---

### **PART 1: THE USER PROFILE (SOURCE OF TRUTH)**

*This data MUST be used to populate `data/profile.json`.*

**A. Personal Identity**
*   **Name:** Pranav Gupta
*   **Email:** `pranavgupta5581@gmail.com` (Personal) / `pranav@seas.upenn.edu` (University)
*   **Phone:** (XXX) XXX-XXXX (Placeholder to be filled in `profile.json`)
*   **Location:** Philadelphia, PA (University) / Dallas, TX (Home)
*   **Links:**
    *   LinkedIn: `linkedin.com/in/pgupta55`
    *   GitHub: `github.com/pranavgupta55`
    *   Portfolio: `pranavgupta.co`

**B. Education History**
1.  **University of Pennsylvania (Philadelphia, PA)**
    *   **Degrees:** Candidate for MSE in Robotics AND BSE in Artificial Intelligence (Data Science Minor).
    *   **Dates:** August 2025 – May 2029 (Master's) / May 2026 (Bachelor's expected).
    *   **Coursework:** Mathematical Foundations of CS, Calculus III, AI Lab.
    *   **Clubs:** PennAiR Software Division, AI@Penn Research & Development, AIBC Development Division.
2.  **School of Science and Engineering (Dallas, TX)**
    *   **Level:** High School.
    *   **Metrics:** SAT 1580, GPA 4.58.
    *   **Honors:** National Merit Scholarship Finalist, 3x UIL State Champion (Math & Science).

**C. Technical Skills Arsenal**
*   **Languages:** Python (Expert), C++, OCaml, Java, JavaScript, SQL, HTML/CSS.
*   **Frameworks/Libraries:** React, FastAPI, PyTorch, Pandas, LangChain, Node.js, Tailwind CSS, TensorFlow/Keras, ROS (Robot Operating System).
*   **Tools/Platforms:** Git, Docker, PostgreSQL, Supabase, OpenAI API, Vercel.
*   **Engineering/CAD:** Fusion 360 (Advanced), Onshape, SolidWorks, Welding, Angle Grinding.
*   **Domains:** Computer Vision, Full-stack LLM Integration, RAG (Retrieval Augmented Generation), Reinforcement Learning (PPO/DQN), CNNs, LSTMs.

**D. Key Experience (For Cover Letter Injection)**
1.  **Autonomous Driving Research Intern (University of Texas at Dallas)**
    *   **Role:** Student Intern & First Author.
    *   **Dates:** June–Sep 2024.
    *   **Impact:** Authored and published an ML research paper in Curieux Academic Journal.
    *   **Technical Metric:** Reduced training times on large models from **36 GPU hours to 24 GPU hours** while preserving accuracy.
    *   **Tech Stack:** Python, TensorFlow, TensorBoard, Pandas, nuScenes dataset (800k datapoints).
2.  **Co-Founder & Co-Captain (National Solar Car Challenge)**
    *   **Dates:** Aug 2022 – Present.
    *   **Leadership:** Led a 9-person team in design and manufacturing.
    *   **Business Metric:** Raised **$6,500+** in funding; secured **17+ sponsors**; registered as 501(c)(3).
    *   **Engineering:** Built a one-seater solar car (45 mph top speed).
    *   **Outcome:** Placed **4th Nationally** in 2025 (only the second year as a team).
    *   **Skills:** CAD modeling (Fusion 360), chassis validation, stress analysis.

**E. Projects**
1.  **Recall AI:** Full-stack AI study platform. Built with FastAPI + GPT-4o. Features: Token-saving UX, LangChain structured JSON, RLS (Row Level Security) in PostgreSQL.
2.  **Python Coding Projects:** Created 100+ projects including physics engines and simulations.
3.  **Drone Control RL Agent:** Trained a PPO (Proximal Policy Optimization) agent in PyTorch for drone control in a custom 2D physics simulator.

---

### **PART 2: DETAILED ARCHITECTURE & TECH STACK**

**1. The Stack**
*   **Frontend:** **Streamlit**.
    *   *Why?* Pure Python, rapid development, zero "build" steps, no TypeScript errors.
    *   *Role:* Displays the Job Kanban, Cold Email tools, Calendar, and Settings.
*   **Backend:** **FastAPI** (running via `uvicorn`).
    *   *Why?* Async support (crucial for scraping), robust API definition, separates logic from UI.
    *   *Role:* Handles scraping, AI processing, DB operations, and PDF generation.
*   **Database:** **SQLite**.
    *   *Why?* Single file (`jobs.db`), portable, zero-config, reliable.
    *   *Library:* `sqlite-utils` or standard `sqlite3`.
*   **AI Engine:** **OpenAI API** (`gpt-4o-mini`).
    *   *Why?* Cheap, fast, sufficient reasoning capabilities for tagging and text generation.
*   **Scraping Engine:** **Playwright** + **Requests**.
    *   *Playwright:* For rendering JavaScript-heavy career pages (Workday, Greenhouse, etc.) to extract text.
    *   *Requests/BeautifulSoup:* For scraping the static GitHub Markdown tables.
*   **PDF Engine:** **ReportLab**.
    *   *Why?* Programmatic PDF creation. Allows pixel-perfect replication of formatting (Times New Roman, 11pt, margins) to match existing documents.

**2. Directory Structure**
```text
intern-bot/
├── backend/               # The "Brain"
│   ├── main.py            # API Routes
│   ├── scraper.py         # Job Discovery Logic
│   ├── analyzer.py        # LLM Logic (Tags, Cover Letter)
│   ├── pdf_engine.py      # PDF Generation Logic
│   ├── email_engine.py    # Email Pattern & Verification
│   └── db.py              # Database Interface
├── frontend/              # The "Face"
│   ├── app.py             # Streamlit Entry Point
│   └── components.py      # UI Widgets
├── data/                  # The "Memory"
│   ├── jobs.db            # SQLite File
│   ├── profile.json       # User Profile
│   ├── answers.json       # Behavioral Question Bank
│   └── resumes/           # Folder for PDF Resume Variants
└── templates/             # Assets
    └── cover_letter_template.txt
```

---

### **PART 3: THE WORKFLOW PIPELINES**

#### **Pipeline A: Job Discovery & Ingestion**
1.  **Automated Source (The "Sync"):**
    *   The user clicks "Sync Jobs" in Streamlit.
    *   **Target:** `SimplifyJobs/Summer2026-Internships` and `SimplifyJobs/New-Grad-Positions` (GitHub).
    *   **Process:** Fetch raw README.md -> Parse Markdown Table -> Extract `Company`, `Role`, `Location`, `Link`.
    *   **Deduplication:** Check `Link` against `jobs.db`. Only add if new.
2.  **Manual Source:**
    *   User inputs a URL (Handshake or Company Career Page) via the UI.
    *   **Handshake Handling:** Treated as a raw link. No automated login (too brittle). The user is expected to be logged in via browser when they eventually click "Apply".
    *   **Enrichment:**
        *   System uses **Playwright** to visit the URL.
        *   Extracts full page text (`innerText`).
        *   Checks for specific keywords: "University of Pennsylvania", "UPenn", "Quaker", "Alumni" -> Sets `penn_connection = True`.

#### **Pipeline B: Analysis & Prioritization**
*   **AI Analysis:** The extracted job description is sent to `gpt-4o-mini`.
*   **Tagging:** AI generates tags (e.g., "Computer Vision", "Backend", "Frontend", "Robotics").
*   **Resume Selection (NOT Generation):**
    *   The user maintains a folder `data/resumes/` containing files like `resume_cv.pdf`, `resume_swe.pdf`.
    *   The AI selects the best filename based on the tags (e.g., Tag "CV" -> Select `resume_cv.pdf`).
*   **Prioritization Logic:**
    *   **Priority 1 (Critical):** Application Deadline < 7 days OR Company is "Prestige" (Google, SpaceX, OpenAI, etc.) OR `penn_connection` is True.
    *   **Priority 2 (High):** Posted < 24 hours ago.
    *   **Priority 3 (Standard):** Everything else.
    *   **Priority 4 (Low):** Rolling applications > 30 days old.

#### **Pipeline C: Asset Generation (The Cover Letter)**
*   **Philosophy:** Modular Construction.
*   **Static Blocks (From `profile.json`):**
    *   Header (Name, Address, Links).
    *   Intro ("I am a student at UPenn...").
    *   Body 1 (Hard Skills): The "Autonomous Driving / Research" experience.
    *   Body 2 (Soft Skills): The "Solar Car / Leadership" experience.
    *   Sign-off ("Sincerely, Pranav Gupta").
*   **Dynamic Block (AI Generated):**
    *   The **"Why This Company"** paragraph.
    *   **Prompt Logic:** "Read the Job Description. Identify 2 core company values. Write a 3-sentence paragraph connecting Pranav's background in [specific project] to these values."
*   **Output:** The system uses `reportlab` to stitch these blocks into `Cover_Letter_{Company}.pdf`. It must look exactly like a handmade Word doc.

#### **Pipeline D: The "Human-in-the-Loop" Execution**
1.  **Dashboard:** User sees the "Ready to Apply" Kanban column.
2.  **Selection:** User clicks a job.
3.  **Review:**
    *   System shows the selected Resume (Filename).
    *   System shows the generated "Why Us" text (Editable).
4.  **Action ("Launch"):**
    *   System generates the final PDF.
    *   System copies the "Why Us" text to the **Clipboard** (for pasting into text boxes).
    *   System opens the **Application Link** in the default browser.
    *   System opens the `data/resumes/` folder in macOS Finder (highlighting the correct file).
5.  **Form Filling:**
    *   User uses **Simplify Copilot** (Browser Extension) for 80% of fields.
    *   User uses **Raycast** (Mac Snippets) for any missing info (`cmd+1` -> Name, etc.).
    *   User drags the resume file from the open Finder window.
    *   User pastes the Cover Letter text (or uploads the PDF).

#### **Pipeline E: Cold Email & Contact Discovery**
*   **Trigger:** User wants to contact a recruiter at "Stripe".
*   **Discovery:**
    1.  **Recruiter Search:** System generates a *Clickable Link* for LinkedIn Search (`site:linkedin.com/in stripe "technical recruiter"`). User finds a name manually (e.g., "Sarah Jones").
    2.  **Email Pattern Inference:** System checks `email-format.com` (via scraping) or defaults to common patterns (e.g., `{first}.{last}@stripe.com`).
    3.  **Candidate Generation:** Generates 10 variants (`sarah.jones`, `sjones`, `sarahj`, etc.).
*   **Verification (The "Safe" Protocol):**
    1.  **Syntax:** Regex check.
    2.  **DNS/MX:** `dnspython` query. Does `stripe.com` accept mail?
    3.  **SMTP Handshake:**
        *   Connect to MX server.
        *   `HELO` -> `MAIL FROM` -> `RCPT TO <candidate>`.
        *   **Safety Rule:** Max 1 check per 2 seconds.
        *   **Interpretation:**
            *   `250 OK`: Likely Valid (or Catch-all).
            *   `550 User Unknown`: Definitely Invalid.
            *   `Block/Timeout`: Abort.
*   **Drafting:**
    *   AI generates a draft email connecting "Solar Car" experience to the Company.
    *   User reviews draft -> Clicks "Send" (which essentially copies to clipboard or triggers a `mailto:` link).
    *   System logs the outreach in `jobs.db`.

---

### **PART 4: VISUALIZATION & TRACKING**

*   **Kanban Board:**
    *   Cols: `New`, `Analysis Ready`, `Applied`, `Rejected`, `Interview`.
    *   Cards display: Company Name, Role, Priority Score (Color Coded), Days since posting.
*   **Timeline/Gantt:**
    *   Visualizes Deadlines.
    *   Visualizes "Date Applied".
*   **Answer Bank:**
    *   A UI tab to view/edit `data/answers.json`.
    *   Stores reusable answers for "Biggest Challenge", "Diversity Statement", etc.
    *   AI uses these as a base for custom question answering.

---

### **PART 5: LEGAL & ETHICAL SAFETY RAILS**

1.  **No Aggressive Scraping:** Do not scrape LinkedIn profiles directly. Use Search Links to let the human view the page.
2.  **SMTP Safety:** Never "hammer" a mail server. Use aggressive delays. Handle "Catch-all" responses gracefully (mark as "Risky" rather than "Verified").
3.  **Spam Compliance:** Cold emails must be low volume (20-30/week), targeted, and non-deceptive.
4.  **Handshake:** Do not attempt to automate University SSO login. It requires 2FA and is too brittle. Rely on the user's active browser session.

---

### **PART 6: IMPLEMENTATION PRIORITIES**

1.  **Zero-Bug Deployment:** The generated code must include `requirements.txt` and a setup script. It must use relative paths.
2.  **Error Handling:** If scraping fails (e.g., GitHub is down), the UI should show a Toast message, not crash.
3.  **PDF Quality:** The generated PDF must look professional. Standard fonts, clean margins.
4.  **No Placeholders:** The generated code must contain the **actual** AI prompts, the **actual** resume parsing logic, and the **actual** Streamlit UI code.