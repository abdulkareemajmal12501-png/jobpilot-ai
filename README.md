# 🤖 JobPilot AI

A modular Python application that parses resume PDFs, scrapes job listings, matches skills using NLP, generates compatibility scores, and creates personalized cover letters — all displayed in an interactive Streamlit dashboard.

---

## Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Parser** | Extracts structured data (skills, experience, education) from PDF resumes using `pdfplumber` |
| 🔍 **Job Scraper** | Fetches job details from URLs using `requests` + `BeautifulSoup` |
| 🧠 **NLP Skill Matcher** | Uses `spaCy` word vectors to extract and semantically match skills |
| 📊 **Score Generator** | Weighted scoring algorithm (Skills 50%, Experience 30%, Education 20%) |
| ✍️ **Cover Letter Generator** | Uses OpenAI GPT via `LangChain` to write tailored cover letters |
| 🖥️ **Streamlit Dashboard** | Interactive web UI to upload, analyze, and download results |

---

## Project Structure

```
ai_agent/
├── app.py                      # Streamlit dashboard entry point
├── config.py                   # Centralized configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env                        # Environment variables (API keys)
├── modules/
│   ├── resume_parser.py        # PDF text extraction & section parsing
│   ├── job_scraper.py          # Web scraping for job listings
│   ├── skill_matcher.py        # NLP-based skill extraction & matching
│   ├── score_generator.py      # Weighted compatibility scoring
│   └── cover_letter.py         # LLM integration for cover letters
└── utils/
    └── helpers.py              # Text cleaning, validation, utilities
```

---

## Installation

### 1. Clone / Download the Project

```bash
cd ai_agent
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model

```bash
python -m spacy download en_core_web_md
```

### 5. Configure API Keys (Optional)

Copy `.env.example` to `.env` and add your OpenAI API key for LLM-powered cover letters:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

> **Note:** If no API key is provided, the cover letter generator falls back to a smart template-based approach.

---

## Usage

### Run the Streamlit Dashboard

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### How to Use

1. **Upload Resume** — Select a PDF file from your computer.
2. **Enter Job URL** — Paste a link to a job posting (must be publicly accessible HTML).
3. **Fill Details** — Enter your name, years of experience, and education status.
4. **Click Analyze** — The agent will:
   - Parse your resume
   - Scrape the job listing
   - Match skills using NLP
   - Calculate a compatibility score
   - Generate a personalized cover letter
5. **Download** — Save the cover letter as a `.txt` file.

---

## Scoring Algorithm

The overall compatibility score is a weighted average:

| Dimension | Weight | Logic |
|-----------|--------|-------|
| **Skills Match** | 50% | Percentage of required skills found in resume |
| **Experience** | 30% | Ratio of candidate years vs. required years (capped at 100%) |
| **Education** | 20% | Binary match (100% if met, 40% if not) |

**Assessment Labels:**
- 85-100: **Strong Fit**
- 70-84: **Good Fit**
- 50-69: **Moderate Fit**
- 0-49: **Weak Fit**

---

## Module Details

### `resume_parser.py`
- Uses `pdfplumber` to extract text from all PDF pages.
- Identifies sections (Skills, Experience, Education, Projects, Summary) via regex heuristics.
- Returns a structured dictionary for downstream processing.

### `job_scraper.py`
- Sends HTTP requests with browser-like headers.
- Parses HTML with `BeautifulSoup` to extract title, company, location, description, and requirements.
- Includes fallback heuristics for varying page structures.

### `skill_matcher.py`
- Loads spaCy's medium English model (`en_core_web_md`) with word vectors.
- Extracts skills via keyword matching against a curated vocabulary (500+ tech/soft skills).
- Computes match percentage and semantic similarity.

### `score_generator.py`
- Takes skill match %, experience metrics, and education status.
- Applies configurable weights to produce an overall score.
- Returns both numeric scores and human-readable assessments.

### `cover_letter.py`
- Uses `LangChain` + `ChatOpenAI` for GPT-powered generation.
- Prompt engineering ensures relevance to the specific job and candidate.
- Graceful fallback to a template if the API is unavailable.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | 1.29.0 | Web dashboard |
| `pdfplumber` | 0.10.0 | PDF text extraction |
| `requests` | 2.31.0 | HTTP requests |
| `beautifulsoup4` | 4.12.2 | HTML parsing |
| `spacy` | 3.7.2 | NLP and word vectors |
| `langchain` | 0.1.0 | LLM orchestration |
| `langchain-openai` | 0.0.2 | OpenAI integration |
| `python-dotenv` | 1.0.0 | Environment variables |
| `pandas` | 2.1.4 | Data handling |
| `scikit-learn` | 1.3.2 | ML utilities |
| `numpy` | 1.26.3 | Numerical operations |

---

## Configuration

All settings are centralized in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SPACY_MODEL` | `en_core_web_md` | spaCy language model |
| `SKILLS_WEIGHT` | 0.50 | Weight for skills in scoring |
| `EXPERIENCE_WEIGHT` | 0.30 | Weight for experience in scoring |
| `EDUCATION_WEIGHT` | 0.20 | Weight for education in scoring |
| `DEFAULT_LLM_MODEL` | `gpt-3.5-turbo` | OpenAI model for cover letters |
| `LLM_TEMPERATURE` | 0.7 | Creativity level for LLM |
| `MAX_TOKENS` | 1024 | Max output length for LLM |

---

## Limitations & Notes

- **Job Scraping:** Many modern job sites (LinkedIn, Indeed) use JavaScript rendering or bot protection. This scraper works best with static HTML pages. For production, consider official APIs or Selenium.
- **LLM Costs:** OpenAI API calls incur costs. Set a spending limit in your OpenAI dashboard.
- **spaCy Model:** The medium model (`en_core_web_md`) is ~100MB. Ensure sufficient disk space and bandwidth.

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

Created by Abdul Kareem Ajmal M.

