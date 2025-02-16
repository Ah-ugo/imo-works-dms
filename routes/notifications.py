import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import users_collection, projects_collection
from config import settings
import requests
import json
from bson import ObjectId
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_project_name(project_id):
    # Convert project_id to ObjectId
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    return project.get("project_name", "Unknown Project") if project else "Unknown Project"


def send_email(to_email, subject, message):
    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # Using Gmail SMTP
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        logger.info(f"Email sent successfully to {to_email}!")
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")


def send_upload_notification(document, users):
    project_name = get_project_name(document.project_id)
    subject = f"New Document Uploaded: {document.title}"
    message = f"A new document '{document.title}' has been uploaded to project {project_name}."
    for user in users:
        send_email(user["email"], subject, message)


def send_comment_notification(document, comment, users):
    subject = f"New Comment on Document: {document.title}"
    message = f"A new comment has been added to document '{document.title}': {comment.content}"
    for user in users:
        send_email(user["email"], subject, message)