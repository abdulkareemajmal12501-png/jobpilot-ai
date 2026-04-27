"""
Configuration module for the AI Agent.
Centralizes API keys, model names, file paths, and scoring weights.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# =============================================================================
# PROJECT METADATA
# =============================================================================
PROJECT_NAME = "JobPilot AI"
AUTHOR = "Abdul Kareem Ajmal M"

# =============================================================================
# API KEYS & SECRETS
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# =============================================================================
# FILE PATHS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# =============================================================================
# NLP & MODEL CONFIGURATION
# =============================================================================
SPACY_MODEL = "en_core_web_md"  # Medium-sized English model with word vectors

# =============================================================================
# JOB SCRAPER CONFIGURATION
# =============================================================================
# Default headers to mimic a real browser request
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

REQUEST_TIMEOUT = 15  # seconds

# =============================================================================
# SCORING WEIGHTS (must sum to 1.0)
# =============================================================================
SKILLS_WEIGHT = 0.50
EXPERIENCE_WEIGHT = 0.30
EDUCATION_WEIGHT = 0.20

# =============================================================================
# COVER LETTER GENERATION
# =============================================================================
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 1024

