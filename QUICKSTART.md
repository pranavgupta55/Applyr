# Applyr Quick Start Guide

**Get up and running in 5 minutes**

---

## Step 1: Setup (2 minutes)

```bash
# Run the setup script
./setup.sh

# This will:
# - Create a virtual environment
# - Install all dependencies
# - Install Playwright browsers
# - Create necessary directories
```

---

## Step 2: Configure (1 minute)

```bash
# Add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Copy your resume PDFs
cp ~/path/to/your/resume.pdf data/resumes/resume_general.pdf
```

**Optional**: Create additional resume variants:
- `resume_cv.pdf` - For research/ML jobs
- `resume_backend.pdf` - For backend engineering
- `resume_frontend.pdf` - For frontend/full-stack

---

## Step 3: Run (1 minute)

**Terminal 1 - Backend:**
```bash
./run_backend.sh
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
```

Browser opens to `http://localhost:8501`

---

## Step 4: First Use (1 minute)

### Dashboard View
1. Click **"🔄 Sync Jobs from GitHub"**
2. Wait for sync (10-30 seconds)
3. See jobs appear in "New" column

### Analyze a Job
1. Click **"🔍 Analyze"** on any job
2. Wait for AI analysis (5-10 seconds)
3. Job moves to "Analyzed" column with tags

### Prepare Application
1. Click **"🚀 Prepare"** on analyzed job
2. Review the "Why This Company" paragraph
3. Click **"📄 Generate PDF"**
4. Click **"📋 Copy to Clipboard"**
5. Click **"🔗 Open Application"**
6. Click **"📂 Open Resumes"**

### Submit (Manual)
1. Fill out the application form
2. Use your Simplify extension for autofill
3. Drag resume from Finder
4. Paste cover letter text
5. Submit!

### Mark Complete
1. Return to dashboard
2. Click **"✅ Mark Applied"**
3. Job moves to "Applied" column

---

## Common Commands

```bash
# Start backend
./run_backend.sh

# Start frontend
./run_frontend.sh

# Kill backend if stuck
lsof -ti:8000 | xargs kill -9

# Reinstall Playwright
source venv/bin/activate
playwright install chromium

# View API docs
open http://localhost:8000/docs
```

---

## Troubleshooting

### "Backend not found"
- Make sure `./run_backend.sh` is running in another terminal
- Check `http://localhost:8000` in your browser

### "OpenAI API Error"
- Check your API key in `.env`
- Verify you have credits in your OpenAI account

### "Playwright Error"
- Run: `source venv/bin/activate && playwright install chromium`

### "No jobs synced"
- Check your internet connection
- GitHub repos might be temporarily down

---

## Tips for Maximum Efficiency

### Raycast Snippets
Set up these shortcuts for instant form filling:
- `cmd+1` → Your name
- `cmd+2` → Email
- `cmd+3` → Phone
- `cmd+4` → LinkedIn
- `cmd+5` → GitHub

### Browser Extensions
- **Simplify Copilot**: Auto-fills common fields
- **LastPass/1Password**: Handles login credentials

### Workflow Optimization
1. **Morning**: Sync jobs, analyze high-priority ones
2. **Afternoon**: Prepare and submit 5-10 applications
3. **Evening**: Cold email 2-3 recruiters

---

## What's Next?

### Customize Your Profile
Edit `data/profile.json` to:
- Update contact info
- Add new projects
- Refine cover letter paragraphs

### Build Answer Bank
Add common behavioral questions in the "Answer Bank" tab

### Track Progress
Use the dashboard to monitor:
- Total applications sent
- Response rate
- Interview conversions

---

**You're all set! Start applying to jobs 10x faster.**

Questions? Check [README.md](README.md) for full documentation.
