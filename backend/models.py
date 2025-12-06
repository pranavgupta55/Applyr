"""
Pydantic models for type validation and API contracts.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    NEW = "New"
    ANALYZED = "Analyzed"
    READY_TO_APPLY = "Ready to Apply"
    APPLIED = "Applied"
    REJECTED = "Rejected"
    INTERVIEW = "Interview"


class JobOrigin(str, Enum):
    GITHUB_SIMPLIFY = "GitHub (SimplifyJobs)"
    GITHUB_SPEEDY = "GitHub (SpeedyApply)"
    HANDSHAKE = "Handshake"
    MANUAL = "Manual URL"


class Priority(int, Enum):
    CRITICAL = 1  # Deadline < 7 days OR Prestige company OR Penn connection
    HIGH = 2      # Posted < 24 hours
    STANDARD = 3  # Everything else
    LOW = 4       # Rolling > 30 days old


class EmailStatus(str, Enum):
    VERIFIED = "Verified"
    LIKELY_VALID = "Likely Valid"
    RISKY = "Risky (Catch-all)"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"


class OutreachStatus(str, Enum):
    DRAFTED = "Drafted"
    SENT = "Sent"
    REPLIED = "Replied"
    NO_RESPONSE = "No Response"


# Database Models
class Job(BaseModel):
    id: Optional[int] = None
    company: str
    role: str
    link: str
    origin: JobOrigin
    status: JobStatus = JobStatus.NEW
    priority_score: Priority = Priority.STANDARD
    tags: List[str] = Field(default_factory=list)
    resume_match: Optional[str] = None
    why_us_text: Optional[str] = None
    notes: Optional[str] = None
    date_found: datetime = Field(default_factory=datetime.now)
    date_posted: Optional[datetime] = None
    deadline: Optional[datetime] = None
    date_applied: Optional[datetime] = None
    penn_connection: bool = False


class Company(BaseModel):
    id: Optional[int] = None
    name: str
    domain: Optional[str] = None
    penn_connection: bool = False
    email_pattern: Optional[str] = None


class Contact(BaseModel):
    id: Optional[int] = None
    company_id: int
    name: str
    role: Optional[str] = None
    email: str
    email_status: EmailStatus = EmailStatus.UNKNOWN
    outreach_status: OutreachStatus = OutreachStatus.DRAFTED
    draft_email: Optional[str] = None
    notes: Optional[str] = None


# API Request/Response Models
class ManualJobInput(BaseModel):
    url: str
    company: Optional[str] = None
    role: Optional[str] = None


class AnalysisResult(BaseModel):
    tags: List[str]
    resume_match: str
    priority: Priority
    why_us_paragraph: str
    penn_connection: bool


class EmailCandidates(BaseModel):
    company: str
    domain: str
    candidates: List[dict]  # [{email, status, confidence}]


class ColdEmailDraft(BaseModel):
    recipient_name: str
    recipient_email: str
    subject: str
    body: str
    company: str
