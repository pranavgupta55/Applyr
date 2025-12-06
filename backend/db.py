"""
SQLite database interface using sqlite-utils.
"""
import sqlite3
from sqlite_utils import Database
from typing import List, Optional, Dict
from datetime import datetime
import json
from pathlib import Path

from backend.models import (
    Job, JobStatus, JobOrigin, Priority,
    Company, Contact, EmailStatus, OutreachStatus
)


class JobDatabase:
    def __init__(self, db_path: str = "data/jobs.db"):
        """Initialize database connection and create tables if needed."""
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db = Database(db_path)
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        # Jobs table
        if "jobs" not in self.db.table_names():
            self.db["jobs"].create({
                "id": int,
                "company": str,
                "role": str,
                "link": str,
                "origin": str,
                "status": str,
                "priority_score": int,
                "tags": str,  # JSON array
                "resume_match": str,
                "why_us_text": str,
                "notes": str,
                "date_found": str,
                "date_posted": str,
                "deadline": str,
                "date_applied": str,
                "penn_connection": int,
            }, pk="id")

            # Create index on link for deduplication
            self.db["jobs"].create_index(["link"], unique=True, if_not_exists=True)

        # Companies table
        if "companies" not in self.db.table_names():
            self.db["companies"].create({
                "id": int,
                "name": str,
                "domain": str,
                "penn_connection": int,
                "email_pattern": str,
            }, pk="id")

            self.db["companies"].create_index(["name"], unique=True, if_not_exists=True)

        # Contacts table
        if "contacts" not in self.db.table_names():
            self.db["contacts"].create({
                "id": int,
                "company_id": int,
                "name": str,
                "role": str,
                "email": str,
                "email_status": str,
                "outreach_status": str,
                "draft_email": str,
                "notes": str,
            }, pk="id", foreign_keys=[("company_id", "companies", "id")])

    # ==================== JOB OPERATIONS ====================

    def add_job(self, job: Job) -> Optional[int]:
        """
        Add a new job to the database.
        Returns job ID if successful, None if duplicate.
        """
        try:
            job_dict = {
                "company": job.company,
                "role": job.role,
                "link": job.link,
                "origin": job.origin.value,
                "status": job.status.value,
                "priority_score": job.priority_score.value,
                "tags": json.dumps(job.tags),
                "resume_match": job.resume_match,
                "why_us_text": job.why_us_text,
                "notes": job.notes,
                "date_found": job.date_found.isoformat(),
                "date_posted": job.date_posted.isoformat() if job.date_posted else None,
                "deadline": job.deadline.isoformat() if job.deadline else None,
                "date_applied": job.date_applied.isoformat() if job.date_applied else None,
                "penn_connection": int(job.penn_connection),
            }

            self.db["jobs"].insert(job_dict)
            return self.db["jobs"].last_pk
        except sqlite3.IntegrityError:
            # Duplicate link
            return None

    def get_job(self, job_id: int) -> Optional[Job]:
        """Get a job by ID."""
        try:
            row = self.db["jobs"].get(job_id)
            return self._row_to_job(row)
        except Exception:
            return None

    def get_all_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """Get all jobs, optionally filtered by status."""
        query = "SELECT * FROM jobs"
        params = []

        if status:
            query += " WHERE status = ?"
            params.append(status.value)

        query += " ORDER BY priority_score ASC, date_found DESC"

        rows = self.db.execute(query, params).fetchall()
        return [self._row_to_job(dict(row)) for row in rows]

    def update_job(self, job_id: int, updates: Dict) -> bool:
        """Update a job with given fields."""
        try:
            # Convert datetime objects to ISO strings
            for key, value in updates.items():
                if isinstance(value, datetime):
                    updates[key] = value.isoformat()
                elif key == "tags" and isinstance(value, list):
                    updates[key] = json.dumps(value)
                elif key == "status" and hasattr(value, "value"):
                    updates[key] = value.value
                elif key == "priority_score" and hasattr(value, "value"):
                    updates[key] = value.value

            self.db["jobs"].update(job_id, updates)
            return True
        except Exception as e:
            print(f"Error updating job: {e}")
            return False

    def job_exists(self, link: str) -> bool:
        """Check if a job with this link already exists."""
        result = self.db.execute(
            "SELECT COUNT(*) as count FROM jobs WHERE link = ?", [link]
        ).fetchone()
        return result["count"] > 0

    def _row_to_job(self, row: Dict) -> Job:
        """Convert database row to Job model."""
        return Job(
            id=row["id"],
            company=row["company"],
            role=row["role"],
            link=row["link"],
            origin=JobOrigin(row["origin"]),
            status=JobStatus(row["status"]),
            priority_score=Priority(row["priority_score"]),
            tags=json.loads(row["tags"]) if row["tags"] else [],
            resume_match=row.get("resume_match"),
            why_us_text=row.get("why_us_text"),
            notes=row.get("notes"),
            date_found=datetime.fromisoformat(row["date_found"]),
            date_posted=datetime.fromisoformat(row["date_posted"]) if row.get("date_posted") else None,
            deadline=datetime.fromisoformat(row["deadline"]) if row.get("deadline") else None,
            date_applied=datetime.fromisoformat(row["date_applied"]) if row.get("date_applied") else None,
            penn_connection=bool(row["penn_connection"]),
        )

    # ==================== COMPANY OPERATIONS ====================

    def add_company(self, company: Company) -> int:
        """Add or update a company."""
        company_dict = {
            "name": company.name,
            "domain": company.domain,
            "penn_connection": int(company.penn_connection),
            "email_pattern": company.email_pattern,
        }

        self.db["companies"].insert(company_dict, replace=True)
        return self.db["companies"].last_pk

    def get_company(self, name: str) -> Optional[Company]:
        """Get company by name."""
        try:
            row = self.db.execute(
                "SELECT * FROM companies WHERE name = ?", [name]
            ).fetchone()

            if row:
                return Company(**dict(row))
            return None
        except Exception:
            return None

    # ==================== CONTACT OPERATIONS ====================

    def add_contact(self, contact: Contact) -> int:
        """Add a new contact."""
        contact_dict = {
            "company_id": contact.company_id,
            "name": contact.name,
            "role": contact.role,
            "email": contact.email,
            "email_status": contact.email_status.value,
            "outreach_status": contact.outreach_status.value,
            "draft_email": contact.draft_email,
            "notes": contact.notes,
        }

        self.db["contacts"].insert(contact_dict)
        return self.db["contacts"].last_pk

    def get_contacts_by_company(self, company_id: int) -> List[Contact]:
        """Get all contacts for a company."""
        rows = self.db.execute(
            "SELECT * FROM contacts WHERE company_id = ?", [company_id]
        ).fetchall()

        return [Contact(**dict(row)) for row in rows]

    def update_contact(self, contact_id: int, updates: Dict) -> bool:
        """Update a contact."""
        try:
            # Convert enums to values
            for key, value in updates.items():
                if hasattr(value, "value"):
                    updates[key] = value.value

            self.db["contacts"].update(contact_id, updates)
            return True
        except Exception as e:
            print(f"Error updating contact: {e}")
            return False


# Singleton instance
_db_instance = None

def get_db() -> JobDatabase:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = JobDatabase()
    return _db_instance
