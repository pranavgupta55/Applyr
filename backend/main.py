"""
FastAPI backend for the Applyr internship bot.
Handles all scraping, analysis, and data operations.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
from pathlib import Path
import os
from dotenv import load_dotenv

from backend.models import (
    Job, JobStatus, ManualJobInput, AnalysisResult,
    ColdEmailDraft, EmailCandidates, Company, Contact
)
from backend.db import get_db
from backend.scraper import JobScraper, calculate_priority
from backend.analyzer import JobAnalyzer
from backend.pdf_engine import CoverLetterGenerator
from backend.email_engine import EmailDiscovery, extract_domain_from_company

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Applyr API",
    description="Backend for the Human-in-the-Loop Internship Application Bot",
    version="1.0.0"
)

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = get_db()
scraper = JobScraper()
analyzer = JobAnalyzer()
pdf_gen = CoverLetterGenerator()
email_discovery = EmailDiscovery()


# ==================== UTILITY FUNCTIONS ====================

def load_profile() -> dict:
    """Load user profile data."""
    profile_path = Path("data/profile.json")
    if profile_path.exists():
        with open(profile_path) as f:
            return json.load(f)
    return {}


def load_answers() -> dict:
    """Load behavioral answers bank."""
    answers_path = Path("data/answers.json")
    if answers_path.exists():
        with open(answers_path) as f:
            return json.load(f)
    return {}


def get_available_resumes() -> List[str]:
    """Get list of available resume files."""
    resume_dir = Path("data/resumes")
    if resume_dir.exists():
        return [f.name for f in resume_dir.glob("*.pdf")]
    return ["resume_general.pdf"]


# ==================== JOB ENDPOINTS ====================

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Applyr API",
        "version": "1.0.0"
    }


@app.post("/jobs/sync")
def sync_jobs(background_tasks: BackgroundTasks):
    """
    Sync jobs from GitHub sources.
    Returns count of new jobs added.
    """
    try:
        jobs = scraper.scrape_github_jobs()

        new_count = 0
        for job in jobs:
            # Check if job already exists
            if not db.job_exists(job.link):
                # Calculate priority
                job.priority_score = calculate_priority(job)

                # Add to database
                job_id = db.add_job(job)
                if job_id:
                    new_count += 1

        return {
            "status": "success",
            "total_found": len(jobs),
            "new_jobs": new_count,
            "message": f"Added {new_count} new jobs"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.post("/jobs/manual")
def add_manual_job(job_input: ManualJobInput):
    """
    Add a manual job URL (Handshake or Company page).
    Enriches with scraped data.
    """
    try:
        # Check if already exists
        if db.job_exists(job_input.url):
            raise HTTPException(status_code=400, detail="Job already exists")

        # Enrich the job
        job = scraper.enrich_manual_job(
            url=job_input.url,
            company=job_input.company,
            role=job_input.role
        )

        if job is None:
            raise HTTPException(status_code=500, detail="Failed to scrape job details")

        # Calculate priority
        job.priority_score = calculate_priority(job)

        # Add to database
        job_id = db.add_job(job)

        if job_id:
            return {
                "status": "success",
                "job_id": job_id,
                "company": job.company,
                "role": job.role,
                "penn_connection": job.penn_connection
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add job to database")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/jobs", response_model=List[Job])
def get_jobs(status: Optional[str] = None):
    """Get all jobs, optionally filtered by status."""
    try:
        if status:
            jobs = db.get_all_jobs(status=JobStatus(status))
        else:
            jobs = db.get_all_jobs()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int):
    """Get a specific job by ID."""
    job = db.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/jobs/{job_id}/analyze")
def analyze_job(job_id: int):
    """
    Analyze a job using AI.
    Generates tags, resume match, and why_us paragraph.
    """
    try:
        # Get job
        job = db.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        # Fetch page content for analysis
        page_text = scraper._fetch_page_with_playwright(job.link) or scraper._fetch_page_with_requests(job.link)

        if not page_text:
            raise HTTPException(status_code=500, detail="Could not fetch job description")

        # Get available resumes
        resumes = get_available_resumes()

        # Analyze with AI
        analysis = analyzer.analyze_job(
            job_description=page_text,
            company_name=job.company,
            role=job.role,
            available_resumes=resumes,
            penn_connection=job.penn_connection
        )

        # Update job in database
        db.update_job(job_id, {
            'tags': analysis.tags,
            'resume_match': analysis.resume_match,
            'why_us_text': analysis.why_us_paragraph,
            'priority_score': analysis.priority,
            'status': JobStatus.ANALYZED
        })

        return {
            "status": "success",
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/jobs/{job_id}/generate-assets")
def generate_assets(job_id: int):
    """
    Generate cover letter PDF and text for a job.
    Returns paths and clipboard text.
    """
    try:
        # Get job
        job = db.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        if not job.why_us_text:
            raise HTTPException(status_code=400, detail="Job not analyzed yet. Run /analyze first.")

        # Load profile
        profile = load_profile()

        # Generate PDF
        pdf_path = pdf_gen.generate_cover_letter(
            company_name=job.company,
            role=job.role,
            why_us_paragraph=job.why_us_text,
            profile_data=profile
        )

        # Generate text version
        text_version = pdf_gen.generate_text_only(
            company_name=job.company,
            role=job.role,
            why_us_paragraph=job.why_us_text,
            profile_data=profile
        )

        return {
            "status": "success",
            "pdf_path": pdf_path,
            "text_content": text_version,
            "why_us_paragraph": job.why_us_text
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Asset generation failed: {str(e)}")


@app.patch("/jobs/{job_id}")
def update_job(job_id: int, updates: dict):
    """Update a job with arbitrary fields."""
    try:
        success = db.update_job(job_id, updates)
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Update failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ==================== EMAIL/CONTACT ENDPOINTS ====================

@app.post("/contacts/discover")
def discover_contacts(company_name: str, first_name: str, last_name: str):
    """
    Discover and verify email addresses for a contact.
    """
    try:
        # Get or infer domain
        domain = extract_domain_from_company(company_name)

        # Generate candidates
        candidates = email_discovery.generate_email_candidates(
            first_name=first_name,
            last_name=last_name,
            domain=domain
        )

        # Verify (limit checks to avoid hammering)
        verified = email_discovery.verify_candidates(
            candidates=candidates,
            max_checks=5,
            skip_smtp=False  # Set to True for faster results
        )

        return {
            "status": "success",
            "company": company_name,
            "domain": domain,
            "candidates": verified
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


@app.post("/contacts/draft-email")
def draft_email(recipient_name: str, recipient_role: str, company_name: str):
    """
    Generate a cold email draft.
    """
    try:
        draft = analyzer.draft_cold_email(
            recipient_name=recipient_name,
            recipient_role=recipient_role,
            company_name=company_name
        )

        return {
            "status": "success",
            "subject": draft.get("subject", ""),
            "body": draft.get("body", "")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft failed: {str(e)}")


@app.get("/contacts/linkedin-search")
def linkedin_search(company_name: str, role: str = "recruiter"):
    """
    Generate LinkedIn search URL.
    """
    url = email_discovery.generate_linkedin_search_url(company_name, role)
    return {
        "status": "success",
        "search_url": url
    }


# ==================== BEHAVIORAL ANSWERS ENDPOINTS ====================

@app.post("/answers/generate")
def generate_answer(question: str):
    """
    Generate an answer to a behavioral question.
    """
    try:
        answers = load_answers()
        profile = load_profile()

        answer = analyzer.generate_behavioral_answer(
            question=question,
            answer_bank=answers,
            profile_data=profile
        )

        return {
            "status": "success",
            "question": question,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/answers")
def get_answers():
    """Get all stored behavioral answers."""
    return load_answers()


@app.post("/answers")
def save_answers(answers: dict):
    """Save behavioral answers bank."""
    try:
        answers_path = Path("data/answers.json")
        answers_path.parent.mkdir(exist_ok=True)

        with open(answers_path, 'w') as f:
            json.dump(answers, f, indent=2)

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")


# ==================== STATS ENDPOINTS ====================

@app.get("/stats")
def get_stats():
    """Get overall statistics."""
    try:
        all_jobs = db.get_all_jobs()

        stats = {
            "total_jobs": len(all_jobs),
            "by_status": {},
            "by_priority": {},
            "penn_connections": sum(1 for j in all_jobs if j.penn_connection),
        }

        # Count by status
        for job in all_jobs:
            status = job.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # Count by priority
        for job in all_jobs:
            priority = job.priority_score.name
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
