"""
Job Scraper Module
==================
Scrapes job listings from web sources using requests and BeautifulSoup.

Features:
    - Fetch job pages with browser-like headers
    - Extract job title, company, description, requirements
    - Structured output for downstream processing
"""

import re
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from config import DEFAULT_HEADERS, REQUEST_TIMEOUT
from utils.helpers import clean_text, is_valid_url, logger


# =============================================================================
# MAIN CLASS
# =============================================================================

class JobScraper:
    """
    Scraper for job listing pages.

    NOTE: Many job sites (LinkedIn, Indeed) use heavy JavaScript or anti-bot
    measures. This scraper works best with static HTML pages or job boards
    that expose plain HTML. For production use, consider APIs or Selenium.
    """

    def __init__(self, url: str):
        """
        Initialize with a job listing URL.

        Args:
            url (str): Full URL to the job posting.

        Raises:
            ValueError: If the URL is not valid.
        """
        if not is_valid_url(url):
            raise ValueError(f"Invalid URL provided: {url}")
        self.url = url
        self.soup: Optional[BeautifulSoup] = None
        self.job_data: Dict = {}

    def fetch_page(self) -> str:
        """
        Download the HTML content of the job page.

        Returns:
            str: Raw HTML text.

        Raises:
            requests.RequestException: If the HTTP request fails.
        """
        logger.info(f"Fetching job page: {self.url}")
        response = requests.get(
            self.url,
            headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        logger.info(f"Page fetched successfully ({len(response.text)} chars)")
        return response.text

    def parse(self, html: Optional[str] = None) -> Dict:
        """
        Parse job details from HTML.

        Args:
            html (str, optional): Pre-fetched HTML. If None, fetches from URL.

        Returns:
            Dict: Structured job data with keys:
                - title (str)
                - company (str)
                - location (str)
                - description (str)
                - requirements (str)
                - raw_html (str)
        """
        raw_html = html or self.fetch_page()
        self.soup = BeautifulSoup(raw_html, "html.parser")

        # Remove script/style elements
        for element in self.soup(["script", "style"]):
            element.decompose()

        self.job_data = {
            "title": self._extract_title(),
            "company": self._extract_company(),
            "location": self._extract_location(),
            "description": self._extract_description(),
            "requirements": self._extract_requirements(),
            "raw_html": raw_html,
            "url": self.url,
        }

        logger.info(f"Parsed job: {self.job_data['title']} at {self.job_data['company']}")
        return self.job_data

    # -------------------------------------------------------------------------
    # EXTRACTION HELPERS (heuristics-based)
    # -------------------------------------------------------------------------

    def _extract_title(self) -> str:
        """Try common selectors for job title."""
        selectors = [
            "h1", "h2", 
            "[class*='title']", "[class*='job-title']",
            "[class*='heading']",
        ]
        for sel in selectors:
            tag = self.soup.select_one(sel)
            if tag:
                text = clean_text(tag.get_text())
                if 10 < len(text) < 150:
                    return text
        # Fallback to page title
        if self.soup.title:
            return clean_text(self.soup.title.get_text())
        return "Unknown Title"

    def _extract_company(self) -> str:
        """Try common selectors for company name."""
        selectors = [
            "[class*='company']", "[class*='employer']",
            "[class*='organization']",
        ]
        for sel in selectors:
            tag = self.soup.select_one(sel)
            if tag:
                text = clean_text(tag.get_text())
                if 2 < len(text) < 100:
                    return text
        return "Unknown Company"

    def _extract_location(self) -> str:
        """Try common selectors for job location."""
        selectors = [
            "[class*='location']", "[class*='place']",
            "[class*='city']", "[class*='region']",
        ]
        for sel in selectors:
            tag = self.soup.select_one(sel)
            if tag:
                text = clean_text(tag.get_text())
                if 2 < len(text) < 100:
                    return text
        return "Unknown Location"

    def _extract_description(self) -> str:
        """Extract the main job description text."""
        # Try common description containers
        selectors = [
            "[class*='description']", "[class*='details']",
            "[class*='content']", "article", "main",
        ]
        for sel in selectors:
            tag = self.soup.select_one(sel)
            if tag:
                text = clean_text(tag.get_text())
                if len(text) > 200:
                    return text
        # Fallback: largest text block
        return self._largest_text_block()

    def _extract_requirements(self) -> str:
        """
        Extract requirements/qualifications section.
        """
        # Look for a section header followed by content
        keywords = ["requirements", "qualifications", "what you need", "skills required"]
        text = self.soup.get_text(separator="\n")
        pattern = re.compile(
            r"(?i)(" + "|".join(keywords) + r")[\s:\-–—]*\n?(.*?)(?:\n\n|\Z)",
            re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            return clean_text(match.group(2))
        # Fallback: return part of description
        return ""

    def _largest_text_block(self) -> str:
        """Return the largest paragraph/text block as fallback."""
        paragraphs = self.soup.find_all(["p", "div"])
        largest = ""
        for p in paragraphs:
            text = clean_text(p.get_text())
            if len(text) > len(largest):
                largest = text
        return largest


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def scrape_job(url: str) -> Dict:
    """
    One-shot function to scrape a job listing.

    Args:
        url (str): URL of the job posting.

    Returns:
        Dict: Structured job data.
    """
    scraper = JobScraper(url)
    return scraper.parse()

