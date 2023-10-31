from dotenv import load_dotenv,find_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
load_dotenv(dotenv_path)

def send_password_reset_email(email: str, token: str):
    sender_email = os.environ.get("EMAIL_FROM")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    receiver_email = email

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Password Reset Request"

    body = f"Please find below your password reset token:\n\n{token} \n\n Copy it enter it in api alog with your new password\n"
    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()