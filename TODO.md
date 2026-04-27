# Deployment Plan — Push to GitHub & Deploy Website

## Information Gathered
- **Project:** JobPilot AI — Streamlit web app (resume parser, job scraper, NLP skill matcher, score generator, cover letter generator).
- **Current State:** Not a git repository. Git installed (`v2.53.0`). GitHub CLI (`gh`) not installed, but `winget` is available.
- **Target:** Streamlit Community Cloud (free, permanent URL, direct GitHub integration).
- **Key Dependency:** `spacy==3.7.2` + `en_core_web_md` model. Code auto-downloads if missing, but for cloud reliability we pin the model wheel in `requirements.txt`.

## Plan Steps — COMPLETED ✅

1. ✅ **Install GitHub CLI** via `winget install --id GitHub.cli`
2. ✅ **Initialize git repo**, add all files, create initial commit
3. ✅ **Authenticate with GitHub** using PAT
4. ✅ **Create GitHub repo** `jobpilot-ai` and push `main` branch
   - **Repo URL:** `https://github.com/abdulkareemajmal12501-png/jobpilot-ai`
5. ✅ **Add deployment config files:**
   - ✅ Update `requirements.txt` — appended spaCy model wheel URL
   - ✅ Create `.streamlit/config.toml` — app branding & theme
   - ✅ Create `runtime.txt` — pin Python 3.11
6. ✅ **Commit & push** deployment config updates

## Next Step — Deploy on Streamlit Cloud 🚀

Go to **https://share.streamlit.io** and follow these steps:

1. Click **"New app"** (or **"Deploy an app"**)
2. Select your GitHub account: `abdulkareemajmal12501-png`
3. Select repository: `jobpilot-ai`
4. Branch: `main`
5. Main file path: `app.py`
6. Click **"Deploy"**

Streamlit Cloud will automatically:
- Install all dependencies from `requirements.txt`
- Download the spaCy model
- Build and launch your app

You'll get a permanent URL like:  
`https://jobpilot-ai-abcdef.streamlit.app`

## Optional — Enable GPT Cover Letters

If you want AI-generated cover letters (instead of the fallback template):

1. In Streamlit Cloud, go to your app → **Settings** → **Secrets**
2. Add:
   ```
   OPENAI_API_KEY = "sk-your-key-here"
   ```
3. Click **Save** and the app will restart with GPT enabled.

## Files Created/Edited
- `requirements.txt` — appended spaCy model direct download URL
- `.streamlit/config.toml` — new file
- `runtime.txt` — new file
- `TODO.md` — updated with completion status
