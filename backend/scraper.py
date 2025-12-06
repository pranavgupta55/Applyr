"""
Job scraping logic for GitHub sources and manual URL enrichment.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import time

from backend.models import Job, JobOrigin


class JobScraper:
    """Handles job discovery from multiple sources."""

    GITHUB_SOURCES = {
        "SimplifyJobs/Summer2026-Internships": "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md",
        "SimplifyJobs/New-Grad-Positions": "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/README.md",
    }

    PENN_KEYWORDS = [
        "University of Pennsylvania",
        "UPenn",
        "Penn",
        "Quaker",
        "Wharton",
        "Alumni",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    # ==================== GITHUB SCRAPING ====================

    def scrape_github_jobs(self) -> List[Job]:
        """
        Scrape jobs from SimplifyJobs GitHub repositories.
        Returns list of Job objects.
        """
        all_jobs = []

        for source_name, url in self.GITHUB_SOURCES.items():
            try:
                print(f"Scraping {source_name}...")
                jobs = self._parse_github_markdown(url, source_name)
                all_jobs.extend(jobs)
                print(f"  Found {len(jobs)} jobs")
            except Exception as e:
                print(f"  Error scraping {source_name}: {e}")

        return all_jobs

    def _parse_github_markdown(self, url: str, source_name: str) -> List[Job]:
        """
        Parse SimplifyJobs markdown table format.
        Expected format: | Company | Role | Location | Application/Link | Date Posted |
        """
        jobs = []

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            content = response.text

            # Parse markdown table
            lines = content.split('\n')
            in_table = False

            for line in lines:
                # Detect table rows (starts with |)
                if line.strip().startswith('|') and '---' not in line:
                    # Skip header row
                    if 'Company' in line or 'Role' in line:
                        in_table = True
                        continue

                    if not in_table:
                        continue

                    # Parse table row
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]

                    if len(cells) >= 4:
                        company = self._clean_text(cells[0])
                        role = self._clean_text(cells[1])
                        location = self._clean_text(cells[2])
                        link_cell = cells[3]

                        # Extract link from markdown [text](url) format
                        link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', link_cell)
                        if link_match:
                            link = link_match.group(2)
                        else:
                            # Sometimes it's just a plain URL
                            link = self._clean_text(link_cell)

                        # Skip if essential fields are missing
                        if not company or not role or not link or link.startswith('🔒'):
                            continue

                        # Determine origin
                        origin = JobOrigin.GITHUB_SIMPLIFY if "SimplifyJobs" in source_name else JobOrigin.GITHUB_SPEEDY

                        # Create job object
                        job = Job(
                            company=company,
                            role=role,
                            link=link,
                            origin=origin,
                            notes=f"Location: {location}" if location else None,
                            date_found=datetime.now(),
                        )

                        jobs.append(job)

        except Exception as e:
            print(f"Error parsing GitHub markdown: {e}")

        return jobs

    # ==================== MANUAL URL ENRICHMENT ====================

    def enrich_manual_job(self, url: str, company: str = None, role: str = None) -> Optional[Job]:
        """
        Enrich a manually provided job URL by scraping the page.
        Extracts job description and checks for Penn connections.
        """
        try:
            print(f"Enriching manual job: {url}")

            # Use Playwright for JS-heavy pages
            page_text = self._fetch_page_with_playwright(url)

            if not page_text:
                # Fallback to requests for simple pages
                page_text = self._fetch_page_with_requests(url)

            # Try to extract company and role if not provided
            if not company:
                company = self._extract_company_from_url(url)

            if not role:
                role = self._extract_role_from_text(page_text)

            # Check for Penn connection
            penn_connection = self._check_penn_connection(page_text)

            job = Job(
                company=company or "Unknown Company",
                role=role or "Unknown Role",
                link=url,
                origin=JobOrigin.HANDSHAKE if "handshake" in url.lower() else JobOrigin.MANUAL,
                penn_connection=penn_connection,
                date_found=datetime.now(),
            )

            return job

        except Exception as e:
            print(f"Error enriching manual job: {e}")
            return None

    def _fetch_page_with_playwright(self, url: str) -> str:
        """
        Use Playwright to fetch page content (handles JavaScript rendering).
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Set timeout and navigate
                page.goto(url, timeout=30000, wait_until="domcontentloaded")

                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)

                # Extract all text
                text = page.inner_text('body')

                browser.close()
                return text

        except Exception as e:
            print(f"Playwright error: {e}")
            return ""

    def _fetch_page_with_requests(self, url: str) -> str:
        """
        Fallback: use requests + BeautifulSoup for simple pages.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ', strip=True)
            return text

        except Exception as e:
            print(f"Requests error: {e}")
            return ""

    def _check_penn_connection(self, text: str) -> bool:
        """Check if page text contains Penn-related keywords."""
        text_lower = text.lower()
        for keyword in self.PENN_KEYWORDS:
            if keyword.lower() in text_lower:
                return True
        return False

    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL (best effort)."""
        # Extract domain
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            domain = match.group(1)
            # Remove common TLDs and subdomains
            company = domain.replace('.com', '').replace('.io', '').replace('.ai', '')
            company = company.split('.')[0]
            return company.title()
        return "Unknown"

    def _extract_role_from_text(self, text: str) -> str:
        """Extract job role from page text (simple heuristic)."""
        # Look for common patterns
        patterns = [
            r'(Software Engineer.*?Intern)',
            r'(.*?Internship)',
            r'(.*?Engineer)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:100]  # Limit length

        return "Internship"

    def _clean_text(self, text: str) -> str:
        """Clean markdown formatting from text."""
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Remove other markdown
        text = re.sub(r'[*_`]', '', text)
        return text.strip()


# ==================== HELPER FUNCTIONS ====================

def calculate_priority(job: Job, page_text: str = "") -> int:
    """
    Calculate job priority based on multiple factors.
    Returns Priority enum value.
    """
    from backend.models import Priority

    # Priority 1 (Critical): Prestige companies, Penn connections, or tight deadlines
    prestige_companies = [
        'Google', 'SpaceX', 'OpenAI', 'Apple', 'Meta', 'Microsoft',
        'Amazon', 'Tesla', 'Anthropic', 'DeepMind', 'Nvidia'
    ]

    if any(comp.lower() in job.company.lower() for comp in prestige_companies):
        return Priority.CRITICAL

    if job.penn_connection:
        return Priority.CRITICAL

    if job.deadline:
        days_until_deadline = (job.deadline - datetime.now()).days
        if days_until_deadline < 7:
            return Priority.CRITICAL

    # Priority 2 (High): Posted recently
    if job.date_posted:
        hours_since_posted = (datetime.now() - job.date_posted).total_seconds() / 3600
        if hours_since_posted < 24:
            return Priority.HIGH

    # Priority 4 (Low): Old rolling applications
    if job.date_found:
        days_since_found = (datetime.now() - job.date_found).days
        if days_since_found > 30:
            return Priority.LOW

    # Priority 3 (Standard): Everything else
    return Priority.STANDARD
