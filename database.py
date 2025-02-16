from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("MONGO_URL")

# MongoDB Connection
client = MongoClient(url)
db = client["document_management_system"]
users_collection = db["users"]
projects_collection = db["projects"]
documents_collection = db["documents"]
signatures_collection = db["signatures"]
approvals_collection = db["approvals"]
notifications_collection = db["notifications"]
logs_collection = db["logs"]


async def create_indexes():
    # Users indexes
    await users_collection.create_index("email", unique=True)

    # Documents indexes
    await documents_collection.create_index("reference_number", unique=True)
    await documents_collection.create_index("project_id")
    await documents_collection.create_index("title")
    await documents_collection.create_index("created_at")

    # Projects indexes
    await projects_collection.create_index("project_name")
    await projects_collection.create_index("created_by")

    # Approvals indexes
    await approvals_collection.create_index("document_id")
    await approvals_collection.create_index("approved_by")

    # Signatures indexes
    await signatures_collection.create_index("document_id")
    await signatures_collection.create_index("user_id")

    # Notifications indexes
    await notifications_collection.create_index("user_id")
    await notifications_collection.create_index("is_read")

    # Logs indexes
    await logs_collection.create_index("user_id")
    await logs_collection.create_index("document_id")
    await logs_collection.create_index("timestamp")