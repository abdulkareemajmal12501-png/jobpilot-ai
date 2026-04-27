"""
Score Generator Module
======================
Calculates a weighted compatibility score between a candidate
and a job posting based on multiple dimensions.

Dimensions:
    - Skills match (50%)
    - Experience relevance (30%)
    - Education match (20%)

Output:
    - Overall score (0-100)
    - Breakdown per dimension
    - Human-readable assessment
"""

from typing import Dict

from config import EDUCATION_WEIGHT, EXPERIENCE_WEIGHT, SKILLS_WEIGHT
from utils.helpers import logger


# =============================================================================
# SCORING LOGIC
# =============================================================================

class ScoreGenerator:
    """
    Generates a weighted compatibility score for resume vs. job.
    """

    def __init__(
        self,
        skills_match_pct: float,
        experience_years: int = 0,
        required_years: int = 0,
        education_match: bool = False,
    ):
        """
        Initialize with candidate and job metrics.

        Args:
            skills_match_pct (float): Percentage of required skills matched (0-100).
            experience_years (int): Years of experience the candidate has.
            required_years (int): Years of experience required by the job.
            education_match (bool): Whether education requirements are met.
        """
        self.skills_match_pct = max(0.0, min(100.0, skills_match_pct))
        self.experience_years = max(0, experience_years)
        self.required_years = max(0, required_years)
        self.education_match = education_match

    def calculate(self) -> Dict:
        """
        Calculate the overall compatibility score.

        Returns:
            Dict with keys:
                - overall_score (float): Weighted total score (0-100).
                - skills_score (float): Normalized skills score (0-100).
                - experience_score (float): Normalized experience score (0-100).
                - education_score (float): Normalized education score (0-100).
                - assessment (str): Human-readable rating (e.g., "Strong Fit").
        """
        # --- Skills (0-100) ---
        skills_score = self.skills_match_pct

        # --- Experience (0-100) ---
        if self.required_years == 0:
            exp_score = 100.0  # No requirement = full marks
        else:
            ratio = self.experience_years / self.required_years
            if ratio >= 1.5:
                exp_score = 100.0  # Overqualified still gets full marks
            elif ratio >= 1.0:
                exp_score = 90.0 + (ratio - 1.0) * 20  # 90-100
            else:
                exp_score = ratio * 90.0  # Linear up to 90
            exp_score = min(100.0, exp_score)

        # --- Education (0-100) ---
        edu_score = 100.0 if self.education_match else 40.0

        # --- Weighted Overall ---
        overall = (
            skills_score * SKILLS_WEIGHT
            + exp_score * EXPERIENCE_WEIGHT
            + edu_score * EDUCATION_WEIGHT
        )

        result = {
            "overall_score": round(overall, 1),
            "skills_score": round(skills_score, 1),
            "experience_score": round(exp_score, 1),
            "education_score": round(edu_score, 1),
            "assessment": self._assess(overall),
            "details": {
                "experience_years": self.experience_years,
                "required_years": self.required_years,
                "education_match": self.education_match,
            },
        }

        logger.info(
            f"Score: {result['overall_score']} "
            f"(Skills:{skills_score:.0f} Exp:{exp_score:.0f} Edu:{edu_score:.0f})"
        )
        return result

    def _assess(self, score: float) -> str:
        """
        Convert numeric score to a human-readable label.

        Args:
            score (float): Overall score (0-100).

        Returns:
            str: Assessment label.
        """
        if score >= 85:
            return "Strong Fit"
        elif score >= 70:
            return "Good Fit"
        elif score >= 50:
            return "Moderate Fit"
        else:
            return "Weak Fit"


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def generate_score(
    skills_match_pct: float,
    experience_years: int = 0,
    required_years: int = 0,
    education_match: bool = False,
) -> Dict:
    """
    One-shot function to generate a compatibility score.

    Args:
        skills_match_pct (float): Percentage of required skills matched.
        experience_years (int): Candidate's years of experience.
        required_years (int): Job's required years of experience.
        education_match (bool): Whether education requirements are met.

    Returns:
        Dict: Score breakdown and assessment.
    """
    scorer = ScoreGenerator(skills_match_pct, experience_years, required_years, education_match)
    return scorer.calculate()

