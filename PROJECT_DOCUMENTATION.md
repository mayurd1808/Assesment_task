# AI-Powered Business Automation Assistant

## Project Documentation

---

## 1. Project Title

**AI-Powered Business Automation Assistant — Streamlit Version**

---

## 2. Project Overview

The AI-Powered Business Automation Assistant is a web application built to automate business and course-related interactions. This Streamlit implementation provides a complete, self-contained system combining an AI chatbot, a lead capture module, a SQLite database backend, and a protected admin dashboard in a single application.

The project is designed to solve a common business problem: handling repetitive inquiries, capturing leads, and tracking user interactions without relying on manual work. It is especially suitable for training institutes, educational organizations, and service-based businesses that want to improve response speed and lead management.

The system optionally supports Groq API integration for fast, intelligent LLM-based responses, as well as SMTP-based email notification workflows for automated follow-ups after lead submission. The application is deployed and hosted live on Render.

---

## 3. Problem Statement

In many businesses and educational institutes, users repeatedly ask similar questions such as:

- course fees
- course duration
- syllabus details
- admissions eligibility
- available internships and services

At the same time, user inquiries are often collected manually, which makes follow-up slower and less organized.

This project addresses that problem by:

- answering common questions through an AI assistant
- collecting user details through a lead form with validation
- storing lead data in a structured SQLite database
- automatically displaying metrics and lead summaries in an admin dashboard
- allowing admin users to search, delete, and export records

---

## 4. Objectives

The main objectives of this project are:

- to build an AI-powered assistant for business, course, admissions, internship, fee, and service queries
- to capture user inquiries through a validated lead form
- to store lead data in a durable local SQLite database
- to provide a protected admin interface for monitoring leads and exporting data
- to optionally integrate with Groq API for fast, advanced conversational responses
- to optionally support SMTP email notifications for automated lead follow-up
- to deploy the application as a publicly accessible web application on Render

---

## 5. Key Features

- AI chatbot for course, admissions, internship, fee, and service queries
- optional Groq API integration for fast, intelligent LLM-based responses
- built-in demo responses for use without API keys
- lead capture form with input validation
- SQLite database for durable local storage
- admin dashboard with metrics and summary cards
- lead search functionality within the admin panel
- lead deletion capability from the admin panel
- CSV export for captured lead records
- optional SMTP email notification workflow with demo mode fallback
- password-protected admin panel separate from the public interface
- Streamlit-based web interface accessible at localhost

---

## 6. Technology Stack

The project uses the following technologies:

- **Python** for backend logic and application flow
- **Streamlit** for the web interface
- **SQLite** for local lead and log storage
- **Groq API** (optional) for fast LLM-based chatbot responses
- **Render** for live application hosting and deployment
- **SMTP** (optional) for email notification automation
- **CSV** for lead data export
- **Markdown** for documentation

---

## 7. System Modules

### 7.1 Assistant Module

This module allows users to ask questions related to:

- courses and syllabus
- admissions process and eligibility
- available internships
- fee structures
- general business services

The chatbot works in two layers:

1. If a Groq API key is configured (`GROQ_API_KEY`), the app uses Groq to generate fast, natural, context-aware responses.
2. If no API key is provided, the chatbot falls back to built-in demo responses covering common query categories.

### 7.2 Lead Capture Module

This module collects user details through a separate inquiry form with field-level validation.

Fields include:

- full name
- email address
- phone number
- interested course or service
- message or inquiry

Validation ensures required fields are filled before submission is accepted.

### 7.3 Data Storage Module

The application uses **SQLite** as its primary storage layer, providing durable local storage without requiring any external database service.

Two main tables are used:

- `leads` — stores submitted inquiry records
- `automation_logs` — stores workflow and event activity

SQLite is used for both local development and local deployment, making setup straightforward without cloud configuration.

### 7.4 Email Notification Module

When a user submits the inquiry form, the application can optionally trigger an email notification workflow.

- If SMTP credentials (`EMAIL_USER`, `EMAIL_PASS`, `ADMIN_EMAIL`) are configured, a real email notification is sent to the admin.
- If email credentials are not configured, the system displays the workflow in demo mode to illustrate the automation without sending actual emails.

### 7.5 Admin Panel

The admin panel is password-protected and separated from the public user interface.

It allows the admin to:

- view summary metrics for total leads
- search through captured lead records
- delete individual lead entries
- export all lead data as a CSV file
- view recent automation logs and workflow activity

The panel is only accessible when `ADMIN_PASSWORD` is set in the environment variables.

---

## 8. Workflow

The project has three main user paths:

### 8.1 Assistant Flow

- user opens the Assistant view
- enters a question related to courses, admissions, fees, or services
- app checks whether a Groq API key is available
- if available, Groq API generates a fast, natural response
- if not available, built-in demo responses are used
- final answer is shown to the user

### 8.2 Submit Inquiry Flow

- user opens the Submit Inquiry view
- fills in the lead capture form
- app validates all required fields
- lead is stored in the SQLite database
- automation log entry is created
- if SMTP is configured, email notification is sent to admin
- if SMTP is not configured, demo mode notification is displayed
- success message is shown to the user

### 8.3 Admin Flow

- user opens the Admin Panel view
- enters the admin password
- system verifies password against the configured value
- admin dashboard loads with summary metrics
- admin can search, view, delete leads, or export as CSV
- automation logs are visible for recent workflow activity

---

## 9. Database Design

### 9.1 Leads Table

The `leads` table stores all submitted inquiry form records.

Fields:

- `id` — unique record identifier (auto-incremented)
- `full_name` — user's full name
- `email` — user's email address
- `phone` — user's phone number
- `interested_course` — course or service the user is inquiring about
- `message` — user's inquiry or message
- `created_at` — timestamp of submission

### 9.2 Automation Logs Table

The `automation_logs` table stores workflow event records.

Fields:

- `id` — unique log identifier (auto-incremented)
- `event_type` — type of event triggered (e.g., lead submission, email sent)
- `details` — additional event details or description
- `created_at` — timestamp of the event

---

## 10. Files in the Project

- `app.py` — main application logic and Streamlit UI
- `requirements.txt` — project dependencies
- `README.md` — quick setup and project overview
- `PROJECT_DOCUMENTATION.md` — detailed project documentation
- `automation_assistant.db` — local SQLite database (auto-created on first run)

---

## 11. Setup Instructions

### 11.1 Local Setup

1. Install Python 3.10 or above.

2. Navigate to the project folder:

```bash
cd streamlit_app
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Create a `.env` file with the following variables (all are optional):

```env
GROQ_API_KEY=your_groq_api_key
EMAIL_USER=your_smtp_email
EMAIL_PASS=your_smtp_password
ADMIN_EMAIL=admin_recipient_email
ADMIN_PASSWORD=admin123
```

5. Run the application:

```bash
python -m streamlit run app.py
```

6. Open the application in your browser at:

```
http://localhost:8501
```

### 11.2 Deployed Setup (Render)

The application is hosted live on **Render**. To deploy:

1. Push the project to a GitHub repository.

2. Log in to [Render](https://render.com) and create a new **Web Service**.

3. Connect your GitHub repository to the Render service.

4. Set the following build and start commands:

```bash
# Build Command
pip install -r requirements.txt

# Start Command
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

5. Add the following environment variables under the Render service settings:

```env
GROQ_API_KEY=your_groq_api_key
EMAIL_USER=your_smtp_email
EMAIL_PASS=your_smtp_password
ADMIN_EMAIL=admin_recipient_email
ADMIN_PASSWORD=your_admin_password
```

6. Deploy the service. Render will provide a public URL to access the live application.

### 11.3 Running Without API Keys

If no API keys are provided, the chatbot automatically uses built-in demo responses. If email credentials are not configured, lead submission still works and the email workflow is shown in demo mode.

---

## 12. Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Optional | API key for Groq LLM integration |
| `EMAIL_USER` | Optional | SMTP email address for sending notifications |
| `EMAIL_PASS` | Optional | SMTP email password |
| `ADMIN_EMAIL` | Optional | Recipient email address for lead notifications |
| `ADMIN_PASSWORD` | Optional | Password for accessing the admin panel |

---

## 13. Security Considerations

- API keys and credentials are stored in `.env` and never hardcoded in the application
- the admin panel is hidden and inaccessible unless `ADMIN_PASSWORD` is configured
- admin access is protected by password verification on every session
- lead records are stored locally in SQLite and are not exposed to external services unless configured
- internal admin views are fully separated from the public assistant and inquiry views

---

## 14. Advantages of the Project

- reduces repetitive manual query handling through AI-driven responses
- captures potential leads in a structured and validated way
- provides a functional automation workflow for email follow-up
- improves response speed for common business inquiries
- keeps lead data organized and exportable
- works fully without API keys using built-in demo responses
- requires no external database or cloud service for core functionality
- separates public and admin views cleanly

---

## 15. Limitations

- the chatbot quality depends on the API provider selected; demo responses are limited in scope
- admin authentication is basic password-based and does not support multi-user or role-based access
- the email notification module requires manual SMTP configuration
- the SQLite database is local-only and not suitable for multi-server or cloud deployments without migration
- course and service data updates require manual changes to the application logic

---

## 16. Future Enhancements

Possible improvements for future versions:

- migrate to PostgreSQL on Render for scalable cloud-compatible storage
- add WhatsApp or SMS automation after lead submission
- add search filters and date range queries in the admin dashboard
- build an interface to manage courses and services dynamically without code changes
- add role-based authentication with multi-admin support
- add analytics charts and reporting for lead trends
- support multiple business categories and use cases beyond courses
- integrate CRM platforms such as HubSpot or Zoho for lead pipeline management

---

## 17. Conclusion

The AI-Powered Business Automation Assistant successfully demonstrates how AI, lead management, automation, and local storage can be integrated into one practical Streamlit application.

It is not only a chatbot, but also a lightweight business workflow system that supports:

- user interaction through a conversational AI interface
- structured inquiry capture with form validation
- automated email notification workflows
- admin monitoring with search, delete, and export capabilities
- flexible deployment on Render as a publicly accessible web application

This makes it a strong project for internship assessment, academic presentation, and real-world business automation use cases.
