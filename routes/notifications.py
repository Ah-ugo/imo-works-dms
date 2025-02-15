import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import users_collection
from config import settings
import requests
import json


async def send_notification(message: str):
    users = await users_collection.find({}, {"email": 1, "expo_push_token": 1}).to_list(None)

    emails = [user["email"] for user in users if "email" in user]
    expo_tokens = [user["expo_push_token"] for user in users if "expo_push_token" in user and user["expo_push_token"]]

    if emails:
        await send_email_notification(emails, message)

    if expo_tokens:
        await send_push_notification(expo_tokens, message)


async def send_email_notification(recipients, message):
    sender_email = settings.SMTP_USER
    sender_password = settings.SMTP_PASSWORD
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT

    subject = "New Document Notification"
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


async def send_push_notification(expo_tokens, message):
    expo_url = "https://exp.host/--/api/v2/push/send"
    headers = {"Content-Type": "application/json"}

    notifications = [{
        "to": token,
        "sound": "default",
        "title": "New Document Alert",
        "body": message
    } for token in expo_tokens]

    try:
        response = requests.post(expo_url, data=json.dumps(notifications), headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send push notification: {str(e)}")
