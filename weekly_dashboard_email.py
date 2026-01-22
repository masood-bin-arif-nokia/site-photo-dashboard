"""
Weekly Site Photo Dashboard Email
---------------------------------
• Sends email via Outlook Desktop (no Graph / no SMTP)
• Retries if Outlook is not running
• Weekly rotating token
"""

import sys
import time
from datetime import datetime
import win32com.client
import pythoncom
from itsdangerous import URLSafeTimedSerializer

# ===============================
# CONFIG
# ===============================
SECRET_KEY = "MY_SUPER_SECRET_KEY_2026"
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 10

PUBLIC_DASHBOARD_BASE_URL = "https://YOUR_STREAMLIT_APP.streamlit.app"

serializer = URLSafeTimedSerializer(SECRET_KEY)

# ===============================
# TOKEN GENERATOR (WEEKLY)
# ===============================
def generate_weekly_token():
    year, week, _ = datetime.utcnow().isocalendar()
    payload = {"week": f"{year}-W{week}"}
    return serializer.dumps(payload)

# ===============================
# EMAIL SENDER
# ===============================
def send_outlook_email(to_emails: str, dashboard_url: str):
    subject = "📊 Weekly Site Photo Dashboard Access"

    html_body = f"""
    <html>
    <body>
        <p>Hello Team,</p>

        <p>Please use the secure link below to access the
        <b>Site Photo Dashboard (FLM View)</b>:</p>

        <p>
            <a href="{dashboard_url}">
                👉 Open Site Photo Dashboard
            </a>
        </p>

        <p><i>This link is valid for one week and should not be shared.</i></p>

        <br>
        <p>Regards,<br>
        FLM Automation</p>
    </body>
    </html>
    """

    pythoncom.CoInitialize()
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = to_emails
    mail.Subject = subject
    mail.HTMLBody = html_body
    mail.Send()
    pythoncom.CoUninitialize()

# ===============================
# MAIN (RETRY SAFE)
# ===============================
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("python weekly_dashboard_email.py <email(s)>")
        sys.exit(1)

    recipients = sys.argv[1]
    token = generate_weekly_token()
    dashboard_url = f"{PUBLIC_DASHBOARD_BASE_URL}/?token={token}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            send_outlook_email(recipients, dashboard_url)
            print("✅ Weekly dashboard email sent successfully")
            print("🔗 Link:", dashboard_url)
            return
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print("❌ All retries exhausted.")
                sys.exit(2)

if __name__ == "__main__":
    main()
