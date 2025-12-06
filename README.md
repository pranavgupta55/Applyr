# Applyr

**Human-in-the-Loop Internship Application Bot**

Automate the tedious prep work (finding jobs, parsing requirements, generating tailored cover letters, drafting emails) while keeping you in control of the final submission.

---

## Features

✅ **Job Discovery**
- Auto-sync from SimplifyJobs GitHub repos
- Manual URL import (Handshake, company career pages)
- Automatic Penn connection detection

✅ **AI Analysis**
- Smart tagging (CV, ML, Robotics, Backend, etc.)
- Resume variant selection
- Priority scoring (Critical/High/Standard/Low)
- Custom "Why This Company" paragraph generation

✅ **Asset Generation**
- Professional PDF cover letters (ReportLab)
- Modular template system
- Clipboard-ready text

✅ **Human-in-the-Loop Workflow**
- Kanban dashboard
- One-click application prep
- macOS integration (Finder, Clipboard, Browser)
- You click "Submit" - not the bot

✅ **Cold Email Outreach**
- LinkedIn search helper
- Email pattern generation
- Safe SMTP verification
- AI-drafted emails

✅ **Behavioral Answer Bank**
- Store reusable STAR answers
- AI-generated custom responses

---

## Tech Stack

- **Frontend:** Streamlit (Python-only, no React/TypeScript)
- **Backend:** FastAPI + Uvicorn
- **Database:** SQLite (single file, portable)
- **AI:** OpenAI GPT-4o-mini
- **Scraping:** Playwright + BeautifulSoup
- **PDF:** ReportLab

---

## Installation

### Prerequisites
- Python 3.11+
- macOS (M4 or Intel)
- OpenAI API key

### Setup

```bash
# 1. Clone the repo
cd Applyr

# 2. Run setup script
./setup.sh

# 3. Add your API key to .env
echo "OPENAI_API_KEY=your-key-here" > .env

# 4. Copy your resume PDFs to data/resumes/
cp ~/path/to/resume_cv.pdf data/resumes/
cp ~/path/to/resume_backend.pdf data/resumes/
```

---

## Usage

### Start the Backend

```bash
./run_backend.sh
```

The API will be available at `http://localhost:8000`

### Start the Frontend

In a new terminal:

```bash
./run_frontend.sh
```

The dashboard will open at `http://localhost:8501`

---

## Workflow

### 1. **Sync Jobs**
- Click "🔄 Sync Jobs from GitHub" in the dashboard
- Or manually add URLs via "➕ Add Manual Job"

### 2. **Analyze**
- Jobs appear in the "New" column
- Click "🔍 Analyze" to run AI analysis
- System generates tags, selects resume, and writes "Why Us" paragraph

### 3. **Prepare Application**
- Jobs move to "Analyzed" column
- Click "🚀 Prepare" to open the detail panel
- Review and edit the "Why Us" text if needed

### 4. **Generate Assets**
- Click "📄 Generate PDF" to create cover letter
- Click "📋 Copy to Clipboard" to copy text
- Click "🔗 Open Application" to open job page
- Click "📂 Open Resumes" to open Finder

### 5. **Submit (You Do This Manually!)**
- Fill out the application form
- Use Simplify Copilot browser extension for autofill
- Use Raycast snippets for quick data entry (`cmd+1` for name, etc.)
- Drag resume from Finder
- Paste cover letter from clipboard

### 6. **Mark Applied**
- Click "✅ Mark Applied" when done
- Job moves to "Applied" column with timestamp

---

## Cold Email Outreach

### 1. Find Contacts
- Enter company name and role
- Click "🔍 Open LinkedIn Search"
- Manually find the recruiter's name on LinkedIn

### 2. Discover Email
- Enter first name, last name, company
- Click "🔍 Find Emails"
- System generates 10 variants and verifies them

### 3. Draft Email
- Click "✍️ Generate Draft"
- AI writes a personalized cold email
- Edit as needed
- Click "📧 Open in Mail" to send

---

## Raycast Setup (Optional but Recommended)

Set up these snippets in Raycast for ultra-fast form filling:

| Shortcut | Content |
|----------|---------|
| `cmd+1` | Pranav Gupta |
| `cmd+2` | pranavgupta5581@gmail.com |
| `cmd+3` | Your phone number |
| `cmd+4` | linkedin.com/in/pgupta55 |
| `cmd+5` | github.com/pranavgupta55 |
| `cmd+6` | pranavgupta.co |

---

## File Structure

```
Applyr/
├── backend/
│   ├── main.py           # FastAPI routes
│   ├── scraper.py        # Job discovery
│   ├── analyzer.py       # AI analysis
│   ├── pdf_engine.py     # PDF generation
│   ├── email_engine.py   # Email verification
│   ├── db.py             # Database interface
│   └── models.py         # Pydantic models
├── frontend/
│   ├── app.py            # Streamlit dashboard
│   └── utils.py          # API helpers
├── data/
│   ├── jobs.db           # SQLite database
│   ├── profile.json      # Your profile data
│   ├── answers.json      # Behavioral answers
│   └── resumes/          # Your resume PDFs
├── temp/                 # Generated PDFs
├── requirements.txt
├── setup.sh
├── run_backend.sh
└── run_frontend.sh
```

---

## Configuration

### Profile Data

Edit `data/profile.json` to customize:
- Contact information
- Education history
- Skills and experience
- Cover letter paragraphs

### Resume Variants

Place multiple resume versions in `data/resumes/`:
- `resume_cv.pdf` - Research/ML focused
- `resume_backend.pdf` - Backend engineering
- `resume_general.pdf` - General SWE

The AI will select the best match based on job requirements.

---

## Safety & Ethics

### Scraping
- GitHub repos are public and intended for sharing
- Career pages are scraped with respectful delays
- No aggressive bot behavior

### Email Verification
- SMTP checks are rate-limited (2 seconds minimum delay)
- Catch-all servers are detected and flagged
- No spam - cold emails are low-volume and targeted

### Handshake
- No automated login attempts
- Relies on your active browser session
- Respects university authentication

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
lsof -ti:8000 | xargs kill -9

# Restart
./run_backend.sh
```

### Frontend can't connect to backend
- Make sure backend is running first
- Check that it's on `http://localhost:8000`
- Look for errors in the backend terminal

### Playwright errors
```bash
# Reinstall browsers
source venv/bin/activate
playwright install chromium
```

### OpenAI API errors
- Check your API key in `.env`
- Verify you have credits in your OpenAI account
- Check rate limits

---

## Development

### Run tests (when available)
```bash
pytest tests/
```

### Format code
```bash
black backend/ frontend/
ruff check backend/ frontend/
```

---

## Roadmap

- [ ] Email templates library
- [ ] Application deadline reminders
- [ ] Interview prep mode
- [ ] Analytics dashboard (acceptance rate, etc.)
- [ ] Export to CSV

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Credits

Built by Pranav Gupta for automating the internship application grind.

**Stack:**
- OpenAI GPT-4o-mini
- FastAPI & Streamlit
- Playwright
- ReportLab
