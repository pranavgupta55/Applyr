"""
AI-powered job analysis using OpenAI GPT-4o-mini.
Handles tagging, resume selection, and cover letter generation.
"""
import os
from typing import List, Dict
from openai import OpenAI
import json
from pathlib import Path

from backend.models import Priority, AnalysisResult


class JobAnalyzer:
    """AI-powered job analysis and content generation."""

    def __init__(self, api_key: str = None):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    # ==================== JOB ANALYSIS ====================

    def analyze_job(
        self,
        job_description: str,
        company_name: str,
        role: str,
        available_resumes: List[str],
        penn_connection: bool = False
    ) -> AnalysisResult:
        """
        Analyze a job description and generate:
        1. Tags (skills/domains)
        2. Resume recommendation
        3. Priority score
        4. "Why This Company" paragraph
        """

        # Build the analysis prompt
        prompt = self._build_analysis_prompt(
            job_description=job_description,
            company_name=company_name,
            role=role,
            available_resumes=available_resumes
        )

        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Determine priority
            priority = self._determine_priority(
                company_name=company_name,
                tags=result.get("tags", []),
                penn_connection=penn_connection
            )

            return AnalysisResult(
                tags=result.get("tags", []),
                resume_match=result.get("resume_match", available_resumes[0]),
                priority=priority,
                why_us_paragraph=result.get("why_us_paragraph", ""),
                penn_connection=penn_connection
            )

        except Exception as e:
            print(f"Error in job analysis: {e}")
            # Return fallback result
            return AnalysisResult(
                tags=["Software Engineering"],
                resume_match=available_resumes[0] if available_resumes else "resume_general.pdf",
                priority=Priority.STANDARD,
                why_us_paragraph="I am excited to contribute to your team's mission.",
                penn_connection=penn_connection
            )

    def _get_system_prompt(self) -> str:
        """System prompt defining the AI's role."""
        return """You are an expert job application analyst for Pranav Gupta, a University of Pennsylvania student pursuing an MSE in Robotics and BSE in Artificial Intelligence.

Your job is to analyze job descriptions and help Pranav optimize his application strategy.

You have access to Pranav's background:
- Education: UPenn (Robotics MSE, AI BSE, graduating 2029/2026)
- Skills: Python, C++, OCaml, React, FastAPI, PyTorch, ROS, Computer Vision, Fusion 360
- Experience:
  1. Autonomous Driving Research Intern (UT Dallas): Published ML paper, reduced training time 36h→24h using TensorFlow/Keras
  2. Co-Founder Solar Car Team: Raised $6.5k, Fusion 360 CAD design, 4th nationally
- Projects: Recall AI (FastAPI/GPT-4o), 100+ Python projects, PPO RL for drone control

Always respond in JSON format."""

    def _build_analysis_prompt(
        self,
        job_description: str,
        company_name: str,
        role: str,
        available_resumes: List[str]
    ) -> str:
        """Build the analysis prompt."""
        resumes_list = "\n".join([f"- {r}" for r in available_resumes])

        return f"""Analyze this job posting:

**Company:** {company_name}
**Role:** {role}

**Job Description:**
{job_description[:3000]}

**Available Resume Variants:**
{resumes_list}

Provide a JSON response with:

1. **tags** (array of strings): 3-5 technical tags from this list based on the job requirements:
   - "Computer Vision"
   - "Machine Learning"
   - "Robotics"
   - "Backend"
   - "Frontend"
   - "Full-Stack"
   - "AI/ML"
   - "Systems"
   - "Research"
   - "Hardware"

2. **resume_match** (string): Choose the best resume from the available list. If there's a "cv" resume and the job mentions research/ML/robotics, choose it. If it's backend/full-stack, choose "backend" or "general".

3. **why_us_paragraph** (string): Write a compelling 3-4 sentence paragraph explaining why Pranav wants to work at {company_name} specifically.

   IMPORTANT INSTRUCTIONS FOR THE "WHY US" PARAGRAPH:
   - Identify 2-3 core company values or mission elements from the job description
   - Connect Pranav's background (Autonomous Driving research OR Solar Car leadership) to these values
   - Be specific - mention actual projects/metrics (e.g., "36h→24h training optimization" or "$6.5k fundraising")
   - Sound genuine and enthusiastic, not generic
   - Do NOT use clichés like "I'm passionate about" - show, don't tell
   - Use active voice and concrete examples

Return ONLY valid JSON in this format:
{{
  "tags": ["tag1", "tag2", "tag3"],
  "resume_match": "filename.pdf",
  "why_us_paragraph": "Your paragraph here..."
}}"""

    def _determine_priority(
        self,
        company_name: str,
        tags: List[str],
        penn_connection: bool
    ) -> Priority:
        """Determine job priority based on company and tags."""
        # Priority 1: Prestige companies or Penn connection
        prestige_companies = [
            'Google', 'SpaceX', 'OpenAI', 'Apple', 'Meta', 'Microsoft',
            'Amazon', 'Tesla', 'Anthropic', 'DeepMind', 'Nvidia', 'Boston Dynamics'
        ]

        if penn_connection:
            return Priority.CRITICAL

        for comp in prestige_companies:
            if comp.lower() in company_name.lower():
                return Priority.CRITICAL

        # Priority 2: Strong skill match (4+ tags)
        if len(tags) >= 4:
            return Priority.HIGH

        # Default to standard
        return Priority.STANDARD

    # ==================== COVER LETTER GENERATION ====================

    def generate_cover_letter_content(
        self,
        company_name: str,
        role: str,
        why_us_paragraph: str,
        profile_data: Dict
    ) -> str:
        """
        Generate the full cover letter text by combining:
        - Static header/intro/body from profile
        - Dynamic "why us" paragraph from AI
        """
        # This is used for the PDF generation and clipboard copy
        # The actual PDF formatting is handled by pdf_engine.py

        header = f"""{profile_data['name']}
{profile_data['address']}
{profile_data['email']}
{profile_data['links']}

Dear {company_name} team,"""

        intro = f"""I am a student at the University of Pennsylvania pursuing an MSE in Robotics and a BSE in Artificial Intelligence, and I'm excited to apply for the {role} at {company_name}. {why_us_paragraph}"""

        # Static body paragraphs from profile
        body_technical = profile_data.get('cover_letter_technical_paragraph', '')
        body_leadership = profile_data.get('cover_letter_leadership_paragraph', '')
        body_skills = profile_data.get('cover_letter_skills_paragraph', '')
        closing = profile_data.get('cover_letter_closing', '')

        full_letter = f"""{header}

{intro}

{body_technical}

{body_leadership}

{body_skills}

{closing}

Sincerely,
{profile_data['name']}"""

        return full_letter

    # ==================== COLD EMAIL DRAFTING ====================

    def draft_cold_email(
        self,
        recipient_name: str,
        recipient_role: str,
        company_name: str,
        company_description: str = ""
    ) -> Dict[str, str]:
        """
        Generate a cold email draft for recruiter outreach.
        Returns {subject, body}
        """
        prompt = f"""Draft a professional cold email for Pranav Gupta to send to {recipient_name}, a {recipient_role} at {company_name}.

Pranav's Background:
- UPenn student (Robotics MSE, AI BSE)
- Published ML research (autonomous driving)
- Co-founded Solar Car team (raised $6.5k, 4th nationally)
- Skills: Python, PyTorch, FastAPI, ROS, Computer Vision

{f"Company Context: {company_description}" if company_description else ""}

Requirements:
- Subject line: Professional, concise, intriguing
- Body: 3-4 short paragraphs
- Tone: Respectful, enthusiastic but not desperate
- Include ONE specific accomplishment (research paper OR solar car)
- Ask for a brief call/coffee chat about opportunities
- Keep it under 150 words

Return JSON format:
{{
  "subject": "subject line",
  "body": "email body text"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional email writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error drafting email: {e}")
            return {
                "subject": f"UPenn Student Interested in {company_name} Opportunities",
                "body": f"Hi {recipient_name},\n\nI'm a UPenn student working on robotics and AI projects. I'd love to learn more about opportunities at {company_name}.\n\nBest,\nPranav"
            }

    # ==================== BEHAVIORAL ANSWER GENERATION ====================

    def generate_behavioral_answer(
        self,
        question: str,
        answer_bank: Dict[str, str],
        profile_data: Dict
    ) -> str:
        """
        Generate a customized answer to a behavioral question,
        using the answer bank as a reference.
        """
        similar_answer = answer_bank.get(question, "")

        prompt = f"""Generate a concise, compelling answer to this behavioral interview question:

**Question:** {question}

**Reference Answer (if available):** {similar_answer}

**Candidate Background:**
- Research: Autonomous Driving ML paper, reduced training 36h→24h
- Leadership: Co-founded Solar Car team, raised $6.5k, 4th nationally
- Technical: Python, PyTorch, FastAPI, ROS, Computer Vision

Requirements:
- Use STAR format (Situation, Task, Action, Result)
- Include specific metrics
- Keep it 80-120 words
- Sound natural and confident

Return just the answer text (not JSON)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a career coach helping prepare interview answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating answer: {e}")
            return similar_answer or "I would approach this situation by..."
