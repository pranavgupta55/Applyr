# Deployment Checklist

Complete these steps to get Applyr running on your Mac M4.

---

## ☐ Phase 1: Installation (5 minutes)

### 1. Run Setup Script
```bash
cd /Users/pranavgupta/VSCodeProjects/Applyr
./setup.sh
```

Expected output: ✅ Virtual environment created, dependencies installed, Playwright browsers downloaded

### 2. Configure API Key
```bash
# Create .env file
cp .env.example .env

# Edit and add your OpenAI API key
nano .env
# or
code .env
```

Add this line:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Copy Resume PDFs
```bash
# Copy your existing resumes to data/resumes/
cp data/resumes/PranavGuptaResumeNewerShorter.pdf data/resumes/resume_general.pdf

# Optional: Create variants
cp data/resumes/PranavGuptaResumeOlderLonger.pdf data/resumes/resume_cv.pdf
```

---

## ☐ Phase 2: First Run (2 minutes)

### 1. Start Backend
```bash
# Terminal 1
./run_backend.sh
```

✅ Look for: `Uvicorn running on http://0.0.0.0:8000`

### 2. Start Frontend
```bash
# Terminal 2 (new terminal window)
./run_frontend.sh
```

✅ Look for: Browser opens to `http://localhost:8501`

### 3. Test Connection
In the Streamlit UI:
- Navigate to "Settings" page
- Click "🧪 Test Backend Connection"
- ✅ Should show "Backend is running!"

---

## ☐ Phase 3: First Job Sync (2 minutes)

### 1. Sync Jobs
- Dashboard page
- Click "🔄 Sync Jobs from GitHub"
- Wait 10-30 seconds

✅ Should see: "Added X new jobs"
✅ Jobs appear in "New" column

### 2. Analyze a Job
- Click "🔍 Analyze" on any job
- Wait 5-10 seconds

✅ Should see: Job moves to "Analyzed" column with tags

### 3. Generate Assets
- Click "🚀 Prepare" on analyzed job
- Review "Why Us" paragraph
- Click "📄 Generate PDF"

✅ Should see: "PDF created: temp/Cover_Letter_CompanyName.pdf"

---

## ☐ Phase 4: Customization (Optional, 10 minutes)

### 1. Update Profile
Edit `data/profile.json`:
- Update phone number
- Verify email addresses
- Customize cover letter paragraphs

### 2. Add Answer Bank
In Streamlit:
- Go to "Answer Bank" page
- Add common questions and answers
- Use STAR format

### 3. Set Up Raycast (Recommended)
Create snippets:
- `cmd+1` → Pranav Gupta
- `cmd+2` → pranavgupta5581@gmail.com
- `cmd+3` → Your phone number
- `cmd+4` → linkedin.com/in/pgupta55
- `cmd+5` → github.com/pranavgupta55
- `cmd+6` → pranavgupta.co

---

## ☐ Phase 5: First Application (5 minutes)

### Full Workflow Test
1. Select a job in "Analyzed" column
2. Click "🚀 Prepare"
3. Review and edit "Why Us" text
4. Click "📄 Generate PDF"
5. Click "📋 Copy to Clipboard"
6. Click "🔗 Open Application"
7. Click "📂 Open Resumes"
8. Fill out application form:
   - Use Simplify Copilot for autofill
   - Use Raycast snippets for data
   - Drag resume from Finder
   - Paste cover letter text
9. Submit application
10. Click "✅ Mark Applied"

✅ Job should move to "Applied" column

---

## ☐ Phase 6: Troubleshooting (If Needed)

### Backend Issues
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill if needed
lsof -ti:8000 | xargs kill -9

# Restart
./run_backend.sh
```

### Playwright Issues
```bash
source venv/bin/activate
playwright install chromium
```

### OpenAI API Issues
- Check API key in `.env`
- Verify credits at https://platform.openai.com/account/usage
- Check rate limits

### Database Issues
```bash
# If database gets corrupted
rm data/jobs.db

# Backend will recreate on next start
./run_backend.sh
```

---

## ☐ Verification Checklist

Before going into production, verify:

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Can sync jobs from GitHub
- [ ] Can add manual job URL
- [ ] AI analysis generates tags
- [ ] Resume selection works
- [ ] "Why Us" paragraph is coherent
- [ ] PDF generates correctly
- [ ] Clipboard copy works
- [ ] Browser opens job URL
- [ ] Finder opens resumes folder
- [ ] Can mark job as applied
- [ ] Database persists between restarts

---

## ☐ Daily Usage Pattern

### Morning (15 minutes)
1. Start backend and frontend
2. Sync jobs from GitHub
3. Analyze 10-20 high-priority jobs
4. Review and prioritize

### Afternoon (1-2 hours)
1. Prepare applications for top 5-10 jobs
2. Customize "Why Us" paragraphs
3. Generate PDFs
4. Submit applications
5. Mark as applied

### Evening (30 minutes)
1. Cold email 2-3 recruiters
2. Update answer bank
3. Review stats

---

## 🎯 Success Criteria

You're ready for production when:
- ✅ Can complete full workflow in <5 minutes per job
- ✅ "Why Us" paragraphs require minimal editing
- ✅ PDFs match your quality standards
- ✅ No errors during sync/analysis
- ✅ Comfortable with the UI flow

---

## 📚 Quick Reference

### Commands
```bash
# Start backend
./run_backend.sh

# Start frontend
./run_frontend.sh

# Stop backend
Ctrl+C (in backend terminal)

# Stop frontend
Ctrl+C (in frontend terminal)

# View API docs
open http://localhost:8000/docs

# Reinstall
./setup.sh
```

### File Locations
- Resumes: `data/resumes/`
- Profile: `data/profile.json`
- Answers: `data/answers.json`
- Database: `data/jobs.db`
- Generated PDFs: `temp/`
- Logs: Terminal output

### URLs
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

---

## 🆘 Getting Help

1. Check [README.md](README.md) for detailed docs
2. Check [QUICKSTART.md](QUICKSTART.md) for quick guide
3. Check [devLogsV1.md](devLogsV1.md) for technical details
4. Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview

---

**Ready to 10x your application speed!**

Last updated: December 6, 2025
