"""
Helper utilities for text cleaning, validation, and common operations.
"""

import re
import logging
from typing import List

# =============================================================================
# LOGGING SETUP
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# TEXT CLEANING
# =============================================================================

def clean_text(raw_text: str) -> str:
    """
    Normalize and clean raw text extracted from PDFs or web pages.

    Steps:
        1. Replace multiple whitespace characters with a single space.
        2. Strip leading/trailing whitespace.
        3. Remove non-printable characters.

    Args:
        raw_text (str): The unprocessed text string.

    Returns:
        str: Cleaned text.
    """
    if not raw_text:
        return ""

    # Replace multiple whitespaces (including newlines/tabs) with a single space
    cleaned = re.sub(r"\s+", " ", raw_text)

    # Remove non-printable characters
    cleaned = re.sub(r"[^\x20-\x7E\n]", "", cleaned)

    return cleaned.strip()


def extract_bullet_points(text: str) -> List[str]:
    """
    Extract bullet-pointed items from a block of text.

    Args:
        text (str): Text containing bullet points.

    Returns:
        List[str]: List of individual bullet point strings.
    """
    # Common bullet markers: •, -, *, →, ◦, numbers like 1.
    bullets = re.split(r"(?:\n|^)\s*(?:[•\-\*→◦]|\d+\.[\)\.:])\s+", text)
    return [b.strip() for b in bullets if b.strip()]


# =============================================================================
# VALIDATION
# =============================================================================

def is_valid_url(url: str) -> bool:
    """
    Check if a string looks like a valid HTTP/HTTPS URL.

    Args:
        url (str): The URL string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = re.compile(
        r"^(https?:\/\/)?"          # protocol
        r"([\da-z\.-]+)"            # domain
        r"(\.([a-z\.]{2,6}))"      # TLD
        r"([\/\w \.-]*)*\/?$",     # path
        re.IGNORECASE,
    )
    return bool(pattern.match(url))


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to a maximum length, appending '...' if truncated.

    Args:
        text (str): Input text.
        max_length (int): Maximum allowed length.

    Returns:
        str: Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."

