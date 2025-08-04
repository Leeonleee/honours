
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/ec2-user/Documents/university/honours/.env")

def send_email_notification(subject, body, sender_email, app_password, recipient_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

sender_email = os.getenv("EMAIL_USER")
app_password = os.getenv("EMAIL_PASS")

send_email_notification(
    subject="✅ Benchmark Completed!",
    body=f"Model: o3\nResults saved to: path",
    sender_email=sender_email,
    app_password=app_password,
    recipient_email="leonlee20031219@gmail.com"
)