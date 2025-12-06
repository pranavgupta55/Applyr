"""
PDF generation engine using ReportLab.
Creates pixel-perfect cover letters matching the SpaceX template format.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
import os
from pathlib import Path
from typing import Dict


class CoverLetterGenerator:
    """Generate professional cover letter PDFs."""

    def __init__(self):
        self.page_width, self.page_height = letter

        # Define custom styles matching the SpaceX template
        self.styles = getSampleStyleSheet()

        # Header style (name and contact info)
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Normal'],
            fontName='Times-Roman',
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=6,
        )

        # Body style (main text)
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontName='Times-Roman',
            fontSize=11,
            alignment=TA_LEFT,
            leading=14,  # Line height
            spaceAfter=12,
        )

        # Greeting style
        self.greeting_style = ParagraphStyle(
            'CustomGreeting',
            parent=self.styles['Normal'],
            fontName='Times-Roman',
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=12,
        )

    def generate_cover_letter(
        self,
        company_name: str,
        role: str,
        why_us_paragraph: str,
        profile_data: Dict,
        output_path: str = None
    ) -> str:
        """
        Generate a cover letter PDF.
        Returns the path to the generated PDF.
        """
        # Create output directory if needed
        if output_path is None:
            output_dir = Path("temp")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"Cover_Letter_{company_name.replace(' ', '_')}.pdf"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        # Build content
        story = []

        # Header (Name and Contact)
        header_lines = [
            profile_data['name'],
            f"{profile_data.get('address_line1', 'Philadelphia, PA')} • {profile_data.get('address_line2', 'Dallas, TX')} • {profile_data['email']}",
        ]

        # Add links if available
        links = []
        if 'linkedin' in profile_data:
            links.append(profile_data['linkedin'])
        if 'website' in profile_data:
            links.append(profile_data['website'])
        if 'github' in profile_data:
            links.append(profile_data['github'])

        if links:
            header_lines.append(" • ".join(links))

        for line in header_lines:
            story.append(Paragraph(line, self.header_style))

        story.append(Spacer(1, 0.2*inch))

        # Greeting
        greeting = f"Dear {company_name} team,"
        story.append(Paragraph(greeting, self.greeting_style))

        # Introduction paragraph (with why_us integrated)
        intro = f"""I am a student at the University of Pennsylvania pursuing an MSE in Robotics and a BSE in Artificial Intelligence, and I'm excited to apply for the {role} at {company_name}. {why_us_paragraph}"""
        story.append(Paragraph(intro, self.body_style))

        # Body Paragraph 1: Technical Accomplishments
        body_para1 = profile_data.get('cover_letter_technical_paragraph',
            """Two accomplishments that best illustrate how I will add value at your company are: (1) my work as an Autonomous Driving Research Intern, where I led data-pipeline and model-training work that produced a first-author publication and reduced training time on large models from 36 GPU hours to 24 GPU hours while preserving accuracy; and (2) co-founding and co-captaining my high school's Solar Car team, where I led a nine-person design and manufacturing effort (raising $6,500+, securing 17+ sponsors), CAD-modeled and validated chassis components in Fusion 360, and helped the team place 4th nationally. Those experiences show my ability to ship technically sophisticated software and systems, optimize performance under tight constraints and short deadlines, and lead multidisciplinary teams through hands-on engineering work."""
        )
        story.append(Paragraph(body_para1, self.body_style))

        # Body Paragraph 2: Technical Skills
        body_para2 = profile_data.get('cover_letter_skills_paragraph',
            """Technically, I contribute value across the stack. I've built full-stack AI systems (FastAPI backends + GPT-based assistants, LangChain integrations, PostgreSQL row-level security), authored many Python projects and PyTorch models (including RL for drone control), and used React/JavaScript for front-end UIs. I'm comfortable with debugging, performance optimization, unit testing, and producing clear system documentation and diagrams. I learn quickly, collaborate effectively, and thrive in environments where requirements evolve rapidly."""
        )
        story.append(Paragraph(body_para2, self.body_style))

        # Closing paragraph
        closing = profile_data.get('cover_letter_closing',
            """I am available for a full-time, on-site internship for the 12+ consecutive week period beginning January 2026 or March 2026, and I would welcome the chance to discuss how my technical background and hands-on leadership can support your software teams."""
        )
        story.append(Paragraph(closing, self.body_style))

        story.append(Spacer(1, 0.2*inch))

        # Signature
        story.append(Paragraph("Sincerely,", self.body_style))
        story.append(Paragraph(profile_data['name'], self.body_style))

        # Build PDF
        doc.build(story)

        return str(output_path)

    def generate_text_only(
        self,
        company_name: str,
        role: str,
        why_us_paragraph: str,
        profile_data: Dict
    ) -> str:
        """
        Generate plain text version for clipboard copy.
        """
        header = f"""{profile_data['name']}
{profile_data.get('address_line1', 'Philadelphia, PA')} • {profile_data.get('address_line2', 'Dallas, TX')} • {profile_data['email']}
{profile_data.get('linkedin', '')} • {profile_data.get('website', '')} • {profile_data.get('github', '')}

Dear {company_name} team,"""

        intro = f"""I am a student at the University of Pennsylvania pursuing an MSE in Robotics and a BSE in Artificial Intelligence, and I'm excited to apply for the {role} at {company_name}. {why_us_paragraph}"""

        body_para1 = profile_data.get('cover_letter_technical_paragraph',
            """Two accomplishments that best illustrate how I will add value at your company are: (1) my work as an Autonomous Driving Research Intern, where I led data-pipeline and model-training work that produced a first-author publication and reduced training time on large models from 36 GPU hours to 24 GPU hours while preserving accuracy; and (2) co-founding and co-captaining my high school's Solar Car team, where I led a nine-person design and manufacturing effort (raising $6,500+, securing 17+ sponsors), CAD-modeled and validated chassis components in Fusion 360, and helped the team place 4th nationally. Those experiences show my ability to ship technically sophisticated software and systems, optimize performance under tight constraints and short deadlines, and lead multidisciplinary teams through hands-on engineering work."""
        )

        body_para2 = profile_data.get('cover_letter_skills_paragraph',
            """Technically, I contribute value across the stack. I've built full-stack AI systems (FastAPI backends + GPT-based assistants, LangChain integrations, PostgreSQL row-level security), authored many Python projects and PyTorch models (including RL for drone control), and used React/JavaScript for front-end UIs. I'm comfortable with debugging, performance optimization, unit testing, and producing clear system documentation and diagrams. I learn quickly, collaborate effectively, and thrive in environments where requirements evolve rapidly."""
        )

        closing = profile_data.get('cover_letter_closing',
            """I am available for a full-time, on-site internship for the 12+ consecutive week period beginning January 2026 or March 2026, and I would welcome the chance to discuss how my technical background and hands-on leadership can support your software teams."""
        )

        full_text = f"""{header}

{intro}

{body_para1}

{body_para2}

{closing}

Sincerely,
{profile_data['name']}"""

        return full_text
