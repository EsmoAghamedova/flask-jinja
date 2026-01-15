import os
import smtplib
from email.message import EmailMessage

FROM_EMAIL = os.getenv("FROM_EMAIL")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"


def send_email(to, subject, body):
    print("EMAIL_ENABLED =", EMAIL_ENABLED)
    print("SMTP_USER =", SMTP_USER)
    print("FROM_EMAIL =", FROM_EMAIL)
    print("SMTP_PASS exists =", bool(SMTP_PASS))

    
    if not EMAIL_ENABLED:
        print(f"[EMAIL DISABLED] To={to} Subject={subject}")
        return

    if not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
        raise RuntimeError("Missing SMTP env vars (SMTP_USER/SMTP_PASS/FROM_EMAIL)")

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)



# import resend

# resend.api_key = os.environ["RESEND_API_KEY"]

# FROM_EMAIL = os.environ["FROM_EMAIL"]

# def send_email(to, subject, body):
#     params = {
#         "from": FROM_EMAIL,
#         "to": [to],
#         "subject": subject,
#         "text": body
#     }
    
#     response = resend.Emails.send(params)
#     print("Resend response:", response)

