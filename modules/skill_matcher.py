"""
Skill Matcher Module
====================
Uses NLP (spaCy) to extract skills from resume and job description,
then computes a similarity score using vector embeddings.

Features:
    - Named Entity Recognition for skill-like terms
    - spaCy word vectors for semantic similarity
    - Configurable matching threshold
"""

import os
from typing import Dict, List, Set, Tuple

import spacy
from spacy.tokens import Doc

from config import SPACY_MODEL
from utils.helpers import clean_text, logger


# =============================================================================
# SKILL VOCABULARY (expandable)
# =============================================================================

# Common technical skills for software/data roles
TECH_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
    "html", "css", "react", "angular", "vue", "node.js", "django",
    "flask", "spring", "express", "fastapi", "rails", "laravel",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "jenkins", "github actions", "ci/cd", "git", "linux", "bash",
    "pandas", "numpy", "scipy", "scikit-learn", "tensorflow",
    "pytorch", "keras", "opencv", "nltk", "spacy", "hugging face",
    "tableau", "power bi", "excel", "spark", "hadoop", "kafka",
    "mongodb", "postgresql", "mysql", "sqlite", "redis", "elasticsearch",
    "graphql", "rest api", "soap", "microservices", "serverless",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data engineering", "data science", "devops", "agile", "scrum",
}

# Soft skills
SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "conflict resolution", "emotional intelligence",
    "project management", "mentoring", "presentation", "negotiation",
}

ALL_SKILLS = TECH_SKILLS | SOFT_SKILLS


# =============================================================================
# NLP SETUP
# =============================================================================

_nlp = None


def get_nlp() -> spacy.Language:
    """
    Lazy-load the spaCy language model.

    Downloads the model if not already present.

    Returns:
        spacy.Language: Loaded spaCy model.
    """
    global _nlp
    if _nlp is None:
        logger.info(f"Loading spaCy model: {SPACY_MODEL}")
        try:
            _nlp = spacy.load(SPACY_MODEL)
        except OSError:
            logger.warning(f"Model {SPACY_MODEL} not found. Downloading...")
            os.system(f"python -m spacy download {SPACY_MODEL}")
            _nlp = spacy.load(SPACY_MODEL)
    return _nlp


# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================

def extract_skills(text: str) -> Set[str]:
    """
    Extract skill mentions from text using a hybrid approach:
    1. Keyword matching against known skill vocabulary.
    2. spaCy noun chunks as fallback.

    Args:
        text (str): Input text (resume or job description).

    Returns:
        Set[str]: Lowercased skill names found in the text.
    """
    text_lower = clean_text(text).lower()
    found: Set[str] = set()

    # 1. Direct keyword matching
    for skill in ALL_SKILLS:
        # Use word boundaries to avoid partial matches
        if re.search(rf"\b{re.escape(skill)}\b", text_lower):
            found.add(skill)

    # 2. spaCy noun chunks for unknown skills
    nlp = get_nlp()
    doc = nlp(text_lower)
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip()
        if 2 > len(phrase) > 30:
            continue
        # Heuristic: if phrase contains common tech words, treat as skill
        if any(tech in phrase for tech in {"programming", "language", "framework", "tool", "platform", "database", "library"}):
            found.add(phrase)

    return found


def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using spaCy word vectors.

    Args:
        text1 (str): First text (e.g., resume description).
        text2 (str): Second text (e.g., job description).

    Returns:
        float: Similarity score between 0.0 and 1.0.
    """
    nlp = get_nlp()
    doc1 = nlp(clean_text(text1))
    doc2 = nlp(clean_text(text2))

    # spaCy already provides a built-in similarity using word vectors
    return float(doc1.similarity(doc2))


# =============================================================================
# MAIN CLASS
# =============================================================================

import re  # imported here to avoid circular reference issues


class SkillMatcher:
    """
    Matches candidate skills against job requirements using NLP.
    """

    def __init__(self, resume_skills: Set[str], job_skills: Set[str]):
        """
        Initialize with extracted skills from both sources.

        Args:
            resume_skills (Set[str]): Skills found in the resume.
            job_skills (Set[str]): Skills required by the job.
        """
        self.resume_skills = {s.lower().strip() for s in resume_skills}
        self.job_skills = {s.lower().strip() for s in job_skills}
        self.matched: Set[str] = set()
        self.missing: Set[str] = set()

    def match(self) -> Dict:
        """
        Perform skill matching and return detailed results.

        Returns:
            Dict with keys:
                - matched_skills (List[str])
                - missing_skills (List[str])
                - match_percentage (float)
                - total_job_skills (int)
                - total_resume_skills (int)
        """
        self.matched = self.resume_skills & self.job_skills
        self.missing = self.job_skills - self.resume_skills

        total_job = len(self.job_skills)
        match_pct = (len(self.matched) / total_job * 100) if total_job > 0 else 0.0

        results = {
            "matched_skills": sorted(self.matched),
            "missing_skills": sorted(self.missing),
            "match_percentage": round(match_pct, 2),
            "total_job_skills": total_job,
            "total_resume_skills": len(self.resume_skills),
        }

        logger.info(
            f"Skill match: {len(self.matched)}/{total_job} "
            f"({match_pct:.1f}%)"
        )
        return results


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def match_skills(resume_text: str, job_text: str) -> Dict:
    """
    End-to-end skill matching from raw texts.

    Args:
        resume_text (str): Full resume text.
        job_text (str): Full job description text.

    Returns:
        Dict: Skill matching results.
    """
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    matcher = SkillMatcher(resume_skills, job_skills)
    return matcher.match()

