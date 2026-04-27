# Deployment Plan — Push to GitHub & Deploy Website

## Information Gathered
- **Project:** JobPilot AI — Streamlit web app (resume parser, job scraper, NLP skill matcher, score generator, cover letter generator).
- **Current State:** Not a git repository. Git installed (`v2.53.0`). GitHub CLI (`gh`) not installed, but `winget` is available.
- **Target:** Streamlit Community Cloud (free, permanent URL, direct GitHub integration).
- **Key Dependency:** `spacy==3.7.2` + `en_core_web_md` model. Code auto-downloads if missing, but for cloud reliability we pin the model wheel in `requirements.txt`.

## Plan Steps

1. **Install GitHub CLI** via `winget install --id GitHub.cli`
2. **Initialize git repo**, add all files, create initial commit
3. **Authenticate with GitHub** (`gh auth login`) — browser window opens for sign-in
4. **Create GitHub repo** `jobpilot-ai` and push `main` branch
5. **Add deployment config files:**
   - Update `requirements.txt` — append spaCy model wheel URL
   - Create `.streamlit/config.toml` — app branding & theme
   - Create `runtime.txt` — pin Python 3.11
6. **Commit & push** deployment config updates
7. **Deploy on Streamlit Cloud** — connect GitHub repo at `share.streamlit.io`, get live URL

## Files to Create/Edit
- `requirements.txt` — append spaCy model direct download URL
- `.streamlit/config.toml` — new file
- `runtime.txt` — new file

## Follow-up After Editing
- User completes `gh auth login` browser authentication
- User signs in to Streamlit Cloud (free, GitHub login) and deploys the repo
- *(Optional)* Set `OPENAI_API_KEY` in Streamlit Cloud secrets for GPT cover letters; app works without it via fallback template

