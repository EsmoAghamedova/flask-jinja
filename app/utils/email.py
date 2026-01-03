import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

FROM_EMAIL = os.environ["FROM_EMAIL"]

def send_email(to, subject, body):
    params = {
        "from": FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "text": body
    }
    
    response = resend.Emails.send(params)
    print("Resend response:", response)

# def send_email(to, subject, body):
#     SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
#     SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
#     SMTP_USER = os.getenv("SMTP_USER")
#     SMTP_PASS = os.getenv("SMTP_PASS")

#     with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
#         server.starttls()
#         server.login(SMTP_USER, SMTP_PASS)
        
#         msg = EmailMessage()
#         msg["From"] = SMTP_USER
#         msg["To"] = to
#         msg["Subject"] = subject
#         msg.set_content(body)
        
#         server.send_message(msg)