"""
Cover Letter Generator Module
=============================
Generates a personalized cover letter using an LLM (OpenAI GPT)
based on resume data and job details.

Features:
    - Context-aware prompt engineering
    - Structured JSON output
    - Fallback to template if LLM is unavailable
"""

import os
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from config import DEFAULT_LLM_MODEL, LLM_TEMPERATURE, MAX_TOKENS, OPENAI_API_KEY
from utils.helpers import logger


# =============================================================================
# PROMPT TEMPLATE
# =============================================================================

COVER_LETTER_PROMPT = """
You are an expert career coach and professional writer. Your task is to write a compelling,
personalized cover letter for a job application.

=== CANDIDATE RESUME SUMMARY ===
Name: {candidate_name}
Key Skills: {skills}
Experience Summary: {experience}
Education: {education}

=== JOB DETAILS ===
Title: {job_title}
Company: {company}
Job Description: {job_description}

=== INSTRUCTIONS ===
1. Write a professional cover letter (250-400 words).
2. Highlight the candidate's most relevant skills and experiences for this specific job.
3. Show genuine enthusiasm for the role and company.
4. Use a professional but warm tone.
5. Include a strong closing call-to-action.
6. Do NOT include addresses, dates, or placeholder text like "[Your Name]".
7. Start directly with "Dear Hiring Manager,".

Generate only the cover letter text.
"""


# =============================================================================
# FALLBACK TEMPLATE (used when LLM is unavailable)
# =============================================================================

FALLBACK_TEMPLATE = """
Dear Hiring Manager,

I am excited to apply for the {job_title} position at {company}. With my background in {skills}, I am confident in my ability to contribute effectively to your team.

Throughout my career, I have developed strong expertise in {top_skill}, which aligns closely with the requirements outlined in your job description. {experience_snippet}

I am particularly drawn to {company} because of its innovative work in the industry, and I am eager to bring my skills in {skills} to help drive continued success.

Thank you for considering my application. I look forward to discussing how my experience and enthusiasm can benefit your team.

Sincerely,
{candidate_name}
"""


# =============================================================================
# MAIN CLASS
# =============================================================================

class CoverLetterGenerator:
    """
    Generates cover letters using an LLM or fallback template.
    """

    def __init__(self, model_name: str = DEFAULT_LLM_MODEL):
        """
        Initialize the generator.

        Args:
            model_name (str): OpenAI model identifier.
        """
        self.model_name = model_name
        self.llm: Optional[ChatOpenAI] = None
        self._init_llm()

    def _init_llm(self) -> None:
        """
        Initialize the LangChain ChatOpenAI client if API key is present.
        """
        if OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=LLM_TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                    openai_api_key=OPENAI_API_KEY,
                )
                logger.info(f"LLM initialized: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")
        else:
            logger.warning("OPENAI_API_KEY not set. Using fallback template.")

    def generate(
        self,
        resume_data: Dict,
        job_data: Dict,
        candidate_name: str = "Applicant",
    ) -> str:
        """
        Generate a cover letter.

        Args:
            resume_data (Dict): Parsed resume output from ResumeParser.
            job_data (Dict): Parsed job output from JobScraper.
            candidate_name (str): Candidate's name (optional).

        Returns:
            str: Generated cover letter text.
        """
        skills = ", ".join(resume_data.get("skills", [])[:10])
        experience = resume_data.get("experience", "")[:500]
        education = resume_data.get("education", "")[:300]

        job_title = job_data.get("title", "the position")
        company = job_data.get("company", "your company")
        job_description = job_data.get("description", "")[:1000]

        if self.llm:
            return self._generate_with_llm(
                candidate_name, skills, experience, education,
                job_title, company, job_description,
            )
        else:
            return self._generate_fallback(
                candidate_name, skills, experience, job_title, company,
            )

    def _generate_with_llm(
        self,
        candidate_name: str,
        skills: str,
        experience: str,
        education: str,
        job_title: str,
        company: str,
        job_description: str,
    ) -> str:
        """
        Use LangChain + OpenAI to generate the cover letter.
        """
        prompt = ChatPromptTemplate.from_template(COVER_LETTER_PROMPT)
        chain = prompt | self.llm

        try:
            response = chain.invoke({
                "candidate_name": candidate_name,
                "skills": skills,
                "experience": experience,
                "education": education,
                "job_title": job_title,
                "company": company,
                "job_description": job_description,
            })
            text = response.content.strip()
            logger.info("Cover letter generated via LLM")
            return text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_fallback(candidate_name, skills, experience, job_title, company)

    def _generate_fallback(
        self,
        candidate_name: str,
        skills: str,
        experience: str,
        job_title: str,
        company: str,
    ) -> str:
        """
        Use the simple template-based fallback.
        """
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        top_skill = skill_list[0] if skill_list else "my field"
        skills_str = ", ".join(skill_list[:3]) if skill_list else "relevant areas"

        # Extract first sentence of experience for snippet
        exp_snippet = experience.split(".")[0] if experience else "I have relevant experience in this area."

        letter = FALLBACK_TEMPLATE.format(
            job_title=job_title,
            company=company,
            skills=skills_str,
            top_skill=top_skill,
            experience_snippet=exp_snippet,
            candidate_name=candidate_name,
        )
        logger.info("Cover letter generated via fallback template")
        return letter.strip()


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def generate_cover_letter(resume_data: Dict, job_data: Dict, candidate_name: str = "Applicant") -> str:
    """
    One-shot function to generate a cover letter.

    Args:
        resume_data (Dict): Parsed resume data.
        job_data (Dict): Parsed job data.
        candidate_name (str): Candidate's name.

    Returns:
        str: Cover letter text.
    """
    gen = CoverLetterGenerator()
    return gen.generate(resume_data, job_data, candidate_name)

