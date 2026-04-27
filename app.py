"""
Streamlit Dashboard - AI Agent
==============================
Interactive web interface for:
    1. Uploading resume PDFs
    2. Entering job listing URLs
    3. Viewing parsed data, skill matches, scores
    4. Downloading generated cover letters

Run with: streamlit run app.py
"""

import os
import tempfile
from typing import Dict

import streamlit as st

from config import TEMP_DIR
from modules.cover_letter import generate_cover_letter
from modules.job_scraper import scrape_job
from modules.resume_parser import parse_resume
from modules.score_generator import generate_score
from modules.skill_matcher import match_skills
from utils.helpers import is_valid_url


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="JobPilot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown(
    """
    <style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; }
    .sub-header { font-size: 1.2rem; color: #555; margin-bottom: 1rem; }
    .score-box { padding: 1rem; border-radius: 0.5rem; text-align: center; font-size: 1.5rem; font-weight: bold; }
    .score-high { background-color: #d4edda; color: #155724; }
    .score-mid { background-color: #fff3cd; color: #856404; }
    .score-low { background-color: #f8d7da; color: #721c24; }
    .skill-match { color: #28a745; font-weight: bold; }
    .skill-miss { color: #dc3545; }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def display_score_card(score_data: Dict):
    """
    Render a styled score card in Streamlit.
    """
    overall = score_data["overall_score"]
    assessment = score_data["assessment"]

    if overall >= 70:
        css_class = "score-high"
    elif overall >= 50:
        css_class = "score-mid"
    else:
        css_class = "score-low"

    st.markdown(
        f'<div class="score-box {css_class}">'
        f"{overall}/100 — {assessment}"
        f"</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Skills", f"{score_data['skills_score']:.0f}%")
    col2.metric("Experience", f"{score_data['experience_score']:.0f}%")
    col3.metric("Education", f"{score_data['education_score']:.0f}%")


def display_skill_breakdown(match_results: Dict):
    """
    Show matched and missing skills with color coding.
    """
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Matched Skills")
        for skill in match_results["matched_skills"]:
            st.markdown(f'<span class="skill-match">• {skill}</span>', unsafe_allow_html=True)
        if not match_results["matched_skills"]:
            st.write("No direct skill matches found.")

    with col2:
        st.subheader("❌ Missing Skills")
        for skill in match_results["missing_skills"]:
            st.markdown(f'<span class="skill-miss">• {skill}</span>', unsafe_allow_html=True)
        if not match_results["missing_skills"]:
            st.write("No missing skills — great match!")


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """
    Main Streamlit application entry point.
    """
    st.markdown('<div class="main-header">🤖 JobPilot AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload your resume, paste a job URL, and get an instant match score + personalized cover letter.</div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SIDEBAR INPUTS
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.header("📄 Inputs")

        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        job_url = st.text_input("Job Listing URL", placeholder="https://example.com/job-posting")
        candidate_name = st.text_input("Your Name", value="Applicant")
        years_exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=3)
        required_years = st.number_input("Required Years (from job)", min_value=0, max_value=50, value=2)
        education_match = st.checkbox("Education Requirements Met?", value=True)

        run_button = st.button("🚀 Analyze Match", type="primary", use_container_width=True)

        st.markdown("---")
        st.caption("Created by Abdul Kareem Ajmal M")

    # -------------------------------------------------------------------------
    # MAIN CONTENT
    # -------------------------------------------------------------------------
    if not run_button:
        st.info("👈 Fill in the sidebar and click **Analyze Match** to begin.")
        return

    # Validate inputs
    if not uploaded_file:
        st.error("Please upload a resume PDF.")
        return
    if not job_url or not is_valid_url(job_url):
        st.error("Please enter a valid job listing URL.")
        return

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # --- Step 1: Parse Resume ---
        status_text.text("📄 Parsing resume...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=TEMP_DIR) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        resume_data = parse_resume(tmp_path)
        progress_bar.progress(20)

        # --- Step 2: Scrape Job ---
        status_text.text("🔍 Scraping job listing...")
        job_data = scrape_job(job_url)
        progress_bar.progress(40)

        # --- Step 3: Skill Matching ---
        status_text.text("🧠 Matching skills with NLP...")
        match_results = match_skills(resume_data["raw_text"], job_data["description"])
        progress_bar.progress(60)

        # --- Step 4: Score Generation ---
        status_text.text("📊 Calculating compatibility score...")
        score_data = generate_score(
            skills_match_pct=match_results["match_percentage"],
            experience_years=years_exp,
            required_years=required_years,
            education_match=education_match,
        )
        progress_bar.progress(80)

        # --- Step 5: Cover Letter ---
        status_text.text("✍️ Generating cover letter...")
        cover_letter = generate_cover_letter(resume_data, job_data, candidate_name)
        progress_bar.progress(100)
        status_text.empty()

        # --- Display Results ---
        st.success("Analysis complete! See results below.")

        # Score Section
        st.header("📊 Match Score")
        display_score_card(score_data)

        # Skills Section
        st.header("🧩 Skill Analysis")
        st.write(f"**Match Percentage:** {match_results['match_percentage']}% ({match_results['total_job_skills']} job skills analyzed)")
        display_skill_breakdown(match_results)

        # Parsed Data Expander
        with st.expander("📝 View Parsed Data"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Resume Highlights")
                st.write("**Skills:**", ", ".join(resume_data.get("skills", [])[:15]) or "N/A")
                st.write("**Experience:**", resume_data.get("experience", "N/A")[:300] + "...")
            with col2:
                st.subheader("Job Details")
                st.write(f"**Title:** {job_data.get('title', 'N/A')}")
                st.write(f"**Company:** {job_data.get('company', 'N/A')}")
                st.write(f"**Location:** {job_data.get('location', 'N/A')}")

        # Cover Letter Section
        st.header("✉️ Generated Cover Letter")
        st.text_area("Cover Letter", value=cover_letter, height=400)
        st.download_button(
            label="📥 Download Cover Letter",
            data=cover_letter,
            file_name=f"cover_letter_{job_data.get('company', 'company').replace(' ', '_')}.txt",
            mime="text/plain",
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)

    finally:
        # Cleanup temp file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()

