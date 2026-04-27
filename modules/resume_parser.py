"""
Resume Parser Module
====================
Extracts structured information from PDF resumes using pdfplumber.

Features:
    - Raw text extraction from PDF
    - Section identification (skills, experience, education)
    - Structured output as Python dictionaries
"""

import os
import re
from typing import Dict, List, Optional

import pdfplumber

from config import TEMP_DIR
from utils.helpers import clean_text, logger


# =============================================================================
# SECTION PATTERNS
# =============================================================================

# Keywords that typically indicate section headers in a resume
SECTION_KEYWORDS = {
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "experience": ["experience", "work experience", "employment", "professional experience", "career history"],
    "education": ["education", "academic background", "qualifications", "degrees"],
    "projects": ["projects", "personal projects", "open source"],
    "summary": ["summary", "professional summary", "objective", "profile"],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _identify_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into sections based on common header keywords.

    Uses regex to find section boundaries and returns a mapping of
    section_name -> section_content.

    Args:
        text (str): Full cleaned resume text.

    Returns:
        Dict[str, str]: Dictionary with keys like 'skills', 'experience', etc.
    """
    # Build a regex that matches any of the section headers (case-insensitive)
    all_keywords = []
    for keywords in SECTION_KEYWORDS.values():
        all_keywords.extend(keywords)

    # Sort by length (descending) so multi-word headers match first
    all_keywords.sort(key=len, reverse=True)
    pattern = r"(?i)\b(" + "|".join(re.escape(k) for k in all_keywords) + r")\b"

    # Find all matches and their positions
    matches = list(re.finditer(pattern, text))

    sections: Dict[str, str] = {}
    for i, match in enumerate(matches):
        section_title = match.group(1).lower().strip()
        start = match.end()

        # Determine end of this section (start of next match or end of text)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()

        # Map the matched title to a canonical section name
        for canonical, keywords in SECTION_KEYWORDS.items():
            if section_title in keywords:
                # If section already exists, append content
                sections[canonical] = sections.get(canonical, "") + "\n" + section_text
                break

    return sections


def _extract_skills_list(skills_text: str) -> List[str]:
    """
    Extract individual skill items from a skills section.

    Splits on common delimiters like commas, bullets, pipes, etc.

    Args:
        skills_text (str): Text from the skills section.

    Returns:
        List[str]: List of cleaned skill strings.
    """
    if not skills_text:
        return []

    # Split on common separators
    raw_items = re.split(r"[,\n|•\-–]+", skills_text)
    skills = [item.strip() for item in raw_items if len(item.strip()) > 1]
    return list(dict.fromkeys(skills))  # Remove duplicates while preserving order


# =============================================================================
# MAIN CLASS
# =============================================================================

class ResumeParser:
    """
    Parses PDF resumes into structured Python dictionaries.
    """

    def __init__(self, pdf_path: str):
        """
        Initialize with the path to a PDF file.

        Args:
            pdf_path (str): Absolute or relative path to the resume PDF.
        """
        self.pdf_path = pdf_path
        self.raw_text: str = ""
        self.sections: Dict[str, str] = {}
        self.parsed_data: Dict = {}

    def extract_text(self) -> str:
        """
        Extract all text from the PDF using pdfplumber.

        Returns:
            str: Concatenated text from all pages.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
        """
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"Resume PDF not found: {self.pdf_path}")

        logger.info(f"Extracting text from: {self.pdf_path}")
        all_text: List[str] = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    all_text.append(page_text)
                logger.debug(f"Processed page {page_num}")

        self.raw_text = clean_text("\n".join(all_text))
        logger.info(f"Extracted {len(self.raw_text)} characters")
        return self.raw_text

    def parse(self) -> Dict:
        """
        Parse the resume and return structured data.

        Returns:
            Dict: Structured resume data containing:
                - raw_text (str)
                - sections (dict)
                - skills (list)
                - experience (str)
                - education (str)
                - summary (str)
        """
        if not self.raw_text:
            self.extract_text()

        self.sections = _identify_sections(self.raw_text)

        self.parsed_data = {
            "raw_text": self.raw_text,
            "sections": self.sections,
            "skills": _extract_skills_list(self.sections.get("skills", "")),
            "experience": self.sections.get("experience", ""),
            "education": self.sections.get("education", ""),
            "summary": self.sections.get("summary", ""),
        }

        logger.info("Resume parsing complete")
        return self.parsed_data


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def parse_resume(pdf_path: str) -> Dict:
    """
    One-shot function to parse a resume PDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        Dict: Parsed resume data.
    """
    parser = ResumeParser(pdf_path)
    return parser.parse()
