"""
Utility functions for the Streamlit frontend.
"""
import requests
from typing import List, Dict, Optional
import subprocess
import os
import pyperclip


API_BASE = "http://localhost:8000"


# ==================== API CALLS ====================

def api_get(endpoint: str):
    """Make a GET request to the API."""
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None


def api_post(endpoint: str, data: dict = None):
    """Make a POST request to the API."""
    try:
        response = requests.post(f"{API_BASE}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None


def api_patch(endpoint: str, data: dict):
    """Make a PATCH request to the API."""
    try:
        response = requests.patch(f"{API_BASE}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None


# ==================== JOB OPERATIONS ====================

def sync_jobs():
    """Sync jobs from GitHub sources."""
    return api_post("/jobs/sync")


def add_manual_job(url: str, company: str = None, role: str = None):
    """Add a manual job URL."""
    data = {"url": url}
    if company:
        data["company"] = company
    if role:
        data["role"] = role
    return api_post("/jobs/manual", data)


def get_all_jobs(status: str = None):
    """Get all jobs, optionally filtered by status."""
    endpoint = "/jobs" if not status else f"/jobs?status={status}"
    return api_get(endpoint)


def get_job(job_id: int):
    """Get a specific job."""
    return api_get(f"/jobs/{job_id}")


def analyze_job(job_id: int):
    """Analyze a job with AI."""
    return api_post(f"/jobs/{job_id}/analyze")


def generate_assets(job_id: int):
    """Generate cover letter assets."""
    return api_post(f"/jobs/{job_id}/generate-assets")


def update_job(job_id: int, updates: dict):
    """Update a job."""
    return api_patch(f"/jobs/{job_id}", updates)


def get_stats():
    """Get statistics."""
    return api_get("/stats")


# ==================== EMAIL OPERATIONS ====================

def discover_emails(company: str, first_name: str, last_name: str):
    """Discover email addresses."""
    return api_post(
        "/contacts/discover",
        {"company_name": company, "first_name": first_name, "last_name": last_name}
    )


def draft_email(recipient_name: str, recipient_role: str, company: str):
    """Draft a cold email."""
    return api_post(
        "/contacts/draft-email",
        {
            "recipient_name": recipient_name,
            "recipient_role": recipient_role,
            "company_name": company
        }
    )


def get_linkedin_search(company: str, role: str = "recruiter"):
    """Get LinkedIn search URL."""
    return api_get(f"/contacts/linkedin-search?company_name={company}&role={role}")


# ==================== ANSWER BANK ====================

def get_answers():
    """Get behavioral answers."""
    return api_get("/answers")


def save_answers(answers: dict):
    """Save behavioral answers."""
    return api_post("/answers", answers)


def generate_answer(question: str):
    """Generate an answer to a question."""
    return api_post("/answers/generate", {"question": question})


# ==================== MACOS INTEGRATION ====================

def copy_to_clipboard(text: str):
    """Copy text to macOS clipboard."""
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Clipboard error: {e}")
        return False


def open_url(url: str):
    """Open URL in default browser."""
    try:
        subprocess.run(["open", url])
        return True
    except Exception as e:
        print(f"Open URL error: {e}")
        return False


def open_folder(path: str):
    """Open folder in Finder and highlight file."""
    try:
        subprocess.run(["open", "-R", path])
        return True
    except Exception as e:
        print(f"Open folder error: {e}")
        return False


def open_resumes_folder():
    """Open the resumes folder in Finder."""
    return open_folder("data/resumes")


# ==================== PRIORITY HELPERS ====================

PRIORITY_COLORS = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "STANDARD": "🟢",
    "LOW": "⚪"
}

PRIORITY_NAMES = {
    1: "CRITICAL",
    2: "HIGH",
    3: "STANDARD",
    4: "LOW"
}


def get_priority_badge(priority_score: int) -> str:
    """Get colored badge for priority."""
    priority_name = PRIORITY_NAMES.get(priority_score, "STANDARD")
    emoji = PRIORITY_COLORS.get(priority_name, "⚪")
    return f"{emoji} {priority_name}"


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d, %Y")
    except:
        return date_str
