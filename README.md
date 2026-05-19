# Streamlit Version

This folder contains a Streamlit implementation of the AI-Powered Business Automation Assistant.

## Features

- AI chatbot for course, admissions, internship, fee, and service queries
- Lead capture form with validation
- SQLite database storage
- Admin dashboard with metrics, search, delete actions, and CSV export
- Optional Gemini/OpenAI integration
- Optional SMTP email notification workflow

## Run Locally

```bash
cd streamlit_app
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open `http://localhost:8501`.

## Optional Environment Variables

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=
OPENAI_API_KEY=
EMAIL_USER=
EMAIL_PASS=
ADMIN_EMAIL=
ADMIN_PASSWORD= admin123
```

Without API keys, the chatbot uses built-in demo responses. Without email credentials, lead submission still works and email automation is shown as demo mode.
