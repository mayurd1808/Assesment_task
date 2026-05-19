import csv
import json
import os
import re
import smtplib
import sqlite3
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from io import StringIO
from pathlib import Path
from urllib import request as urlrequest
from urllib.error import URLError

import streamlit as st

APP_TITLE = "Smart Business AI Assistant"
DB_PATH = Path(__file__).with_name("business_assistant.sqlite3")
COURSES = ["Full Stack Development", "Data Science", "Digital Marketing", "Internship Program", "Business Automation"]

SYSTEM_PROMPT = "You are an AI business assistant helping users with course details, admissions, pricing, internships, and company services. Answer professionally and concisely."
BUSINESS_CONTEXT = """
Institute: SkillBridge Training Institute
Courses: Full Stack Development, Data Science, Digital Marketing, Business Automation
Duration: 8 to 16 weeks depending on the program
Fees: Starting from INR 9,999 with installment options
Internships: Project-based internships are available for eligible learners
Contact: admissions@skillbridge.example, +91 90000 12345
Services: Website development, CRM setup, marketing automation, chatbot automation
"""


def get_setting(name, default=""):
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return os.getenv(name, value or default)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                interest TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def add_lead(name, email, phone, interest, message):
    with connect_db() as connection:
        cursor = connection.execute(
            "INSERT INTO leads (name, email, phone, interest, message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, interest, message, utc_now()),
        )
        return connection.execute("SELECT * FROM leads WHERE id = ?", (cursor.lastrowid,)).fetchone()


def list_leads(search="", interest=""):
    query = "SELECT * FROM leads WHERE 1 = 1"
    params = []
    if search:
        query += " AND (LOWER(name) LIKE ? OR LOWER(email) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(message) LIKE ?)"
        value = f"%{search.lower()}%"
        params.extend([value, value, value, value])
    if interest:
        query += " AND interest = ?"
        params.append(interest)
    query += " ORDER BY created_at DESC"
    with connect_db() as connection:
        return connection.execute(query, params).fetchall()


def delete_lead(lead_id):
    with connect_db() as connection:
        connection.execute("DELETE FROM leads WHERE id = ?", (lead_id,))


def add_chat(user_message, ai_response):
    with connect_db() as connection:
        connection.execute(
            "INSERT INTO chats (user_message, ai_response, created_at) VALUES (?, ?, ?)",
            (user_message, ai_response, utc_now()),
        )


def list_chats():
    with connect_db() as connection:
        return connection.execute("SELECT * FROM chats ORDER BY created_at DESC").fetchall()

    
def delete_chat(chat_id):
    with connect_db() as connection:
        connection.execute("DELETE FROM chats WHERE id = ?", (chat_id,))


def fallback_response(message):
    text = message.lower()
    if any(word in text for word in ["fee", "fees", "price", "cost"]):
        return "Our courses start from INR 9,999, with installment options available. Share your preferred course and our admissions team can send the exact fee structure."
    if any(word in text for word in ["duration", "long", "weeks"]):
        return "Most programs run for 8 to 16 weeks depending on the course and learning mode. Full Stack and Data Science usually include extra project time."
    if "intern" in text:
        return "Yes, eligible learners can join project-based internships after completing core modules and assessments."
    if any(word in text for word in ["contact", "phone", "email", "call"]):
        return "You can contact admissions at admissions@skillbridge.example or call +91 90000 12345."
    if any(word in text for word in ["service", "business", "automation"]):
        return "We provide website development, CRM setup, chatbot automation, marketing automation, and workflow consulting for service businesses."
    return "I can help with course fees, duration, admissions, internships, contact details, and business automation services. Which program or service are you interested in?"


def post_json(url, payload, headers=None):
    body = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(url, data=body, headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    with urlrequest.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def generate_with_grok(message):
    api_key = get_setting("GROK_API_KEY")

    payload = {
        "model": "grok-beta",
        "messages": [
            {
                "role": "system",
                "content": f"{SYSTEM_PROMPT}\n\nBusiness context:\n{BUSINESS_CONTEXT}"
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.4,
        "max_tokens": 300
    }

    data = post_json(
        "https://api.x.ai/v1/chat/completions",
        payload,
        {
            "Authorization": f"Bearer {api_key}"
        }
    )

    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


def generate_ai_response(message):
    try:
        if get_setting("GROK_API_KEY"):
            return generate_with_grok(message) or fallback_response(message)

    except (URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError) as error:
        st.toast(f"Grok AI unavailable. Using fallback response. {error}")

    return fallback_response(message)


def send_lead_emails(lead):
    email_user = get_setting("EMAIL_USER")
    email_pass = get_setting("EMAIL_PASS")
    admin_email = get_setting("ADMIN_EMAIL", email_user)
    if not email_user or not email_pass:
        return "Lead saved. Email credentials are not configured."

    confirmation = EmailMessage()
    confirmation["From"] = email_user
    confirmation["To"] = lead["email"]
    confirmation["Subject"] = "Thanks for contacting SkillBridge Training Institute"
    confirmation.set_content(f"Hi {lead['name']},\n\nThanks for your interest in {lead['interest']}. Our admissions team will contact you soon.")

    admin_notice = EmailMessage()
    admin_notice["From"] = email_user
    admin_notice["To"] = admin_email
    admin_notice["Subject"] = f"New lead: {lead['name']}"
    admin_notice.set_content(f"Name: {lead['name']}\nEmail: {lead['email']}\nPhone: {lead['phone']}\nInterest: {lead['interest']}\nMessage: {lead['message']}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
        server.login(email_user, email_pass)
        server.send_message(confirmation)
        server.send_message(admin_notice)
    return "Confirmation and admin notification emails sent."


def is_valid_email(email):
    return bool(re.match(r"^\S+@\S+\.\S+$", email))


def leads_csv(leads):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name", "email", "phone", "interest", "message", "created_at"])
    writer.writeheader()
    writer.writerows([dict(lead) for lead in leads])
    return output.getvalue()


def apply_styles():
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }
          div[data-testid="stMetric"] { background: #ffffff; border: 1px solid #dce7ee; border-radius: 8px; padding: 14px; }
          div[data-testid="stMetric"] * { color: #17202a !important; }
          div[data-testid="stMetricLabel"] p { color: #17202a !important; font-weight: 700 !important; }
          div[data-testid="stMetricValue"] { color: #0f766e !important; }
          .hero { background: #17202a; color: white; border-radius: 8px; padding: 28px; margin-bottom: 20px; }
          .hero h1 { margin: 0; font-size: 42px; line-height: 1.1; }
          .pill { display: inline-block; background: #f6bd60; color: #17202a; padding: 5px 10px; border-radius: 6px; font-weight: 700; margin-bottom: 18px; }
          a[href^="#"] { display: none !important; visibility: hidden !important; }
          [data-testid="stHeaderActionElements"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_home():
    st.markdown(
        """
        <div class="hero">
          <span class="pill">AI-Powered CRM Assistant</span>
          <h1>Convert course enquiries into organized, automated follow-ups.</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chats = list_chats()
    leads = list_leads()
    today = datetime.now(timezone.utc).date().isoformat()
    today_leads = sum(1 for lead in leads if lead["created_at"].startswith(today))

    metric_cols = st.columns(3)
    metric_cols[0].metric("Total Available Courses", len(COURSES))
    metric_cols[1].metric("Chat Messages", len(chats))
    metric_cols[2].metric("Today Leads", today_leads)


def render_chat():
    st.subheader("AI Chat Assistant")
    st.caption("Ask about fees, duration, admissions, internships, business services, or contact details.")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello. I can help with course fees, duration, internships, admissions, services, and contact details."}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Ask about course duration or internship support")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Typing..."):
                response = generate_ai_response(prompt)
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        add_chat(prompt, response)


def render_lead_form():
    st.subheader("Lead Capture")
    st.caption("Capture enquiry details and trigger the automation workflow.")

    with st.form("lead_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        name = col_a.text_input("Name")
        email = col_b.text_input("Email")
        phone = col_a.text_input("Phone Number")
        interest = col_b.selectbox("Interest", COURSES)
        message = st.text_area("Message", placeholder="I want details about fees, duration, and placement support.")
        submitted = st.form_submit_button("Submit Lead", type="primary")

    if submitted:
        if not all([name.strip(), email.strip(), phone.strip(), interest.strip(), message.strip()]):
            st.error("Please fill all fields.")
        elif not is_valid_email(email.strip()):
            st.error("Please enter a valid email address.")
        else:
            lead = add_lead(name.strip(), email.strip().lower(), phone.strip(), interest, message.strip())
            try:
                automation_status = send_lead_emails(lead)
            except OSError as error:
                automation_status = f"Lead saved, but email automation failed: {error}"
            st.success("Lead captured successfully.")
            st.info(automation_status)


def render_dashboard():
    st.subheader("Admin Dashboard")
    admin_password = get_setting("ADMIN_PASSWORD", "admin123")
    password_col, _ = st.columns([1, 2.4])
    entered_password = password_col.text_input("Admin Password", type="password", value="")
    if entered_password != admin_password:
        return

    search = st.text_input("Search Leads", placeholder="Search by name, email, phone, or message")
    interest = st.selectbox("Filter by Interest", ["", *COURSES], format_func=lambda value: "All interests" if value == "" else value)
    leads = list_leads(search=search, interest=interest)
    chats = list_chats()

    metric_cols = st.columns(3)
    metric_cols[0].metric("Total Leads", len(list_leads()))
    metric_cols[1].metric("Filtered Leads", len(leads))
    metric_cols[2].metric("Chat History", len(chats))

    st.download_button("Download Leads CSV", data=leads_csv(leads), file_name="leads.csv", mime="text/csv", disabled=not leads)

    st.markdown("#### Leads")
    if leads:
        for lead in leads:
            with st.container(border=True):
                cols = st.columns([3, 2, 2, 1])
                cols[0].write(f"**{lead['name']}**  \n{lead['email']}")
                cols[1].write(lead["phone"])
                cols[2].write(lead["interest"])
                if cols[3].button("Delete", key=f"delete-lead-{lead['id']}"):
                    delete_lead(lead["id"])
                    st.rerun()
                st.caption(f"{lead['message']} | {lead['created_at']}")
    else:
        st.info("No leads found.")

    st.markdown("#### Chat History")
    if chats:
        for chat in chats[:50]:
            with st.container(border=True):
                cols = st.columns([5, 1])
                cols[0].write(f"**User:** {chat['user_message']}")
                cols[0].write(f"**Assistant:** {chat['ai_response']}")
                cols[0].caption(chat["created_at"])
                if cols[1].button("Delete", key=f"delete-chat-{chat['id']}"):
                    delete_chat(chat["id"])
                    st.rerun()
    else:
        st.info("No chat history yet.")


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    init_db()
    apply_styles()

    st.sidebar.title(APP_TITLE)
    page = st.sidebar.radio("Navigation", ["Home", "AI Chat", "Client Inquiry Form", "Dashboard"])

    if page == "Home":
        render_home()
    elif page == "AI Chat":
        render_chat()
    elif page == "Client Inquiry Form":
        render_lead_form()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()

