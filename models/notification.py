from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from database import notifications_collection


def convert_id(obj):
    if "_id" in obj:
        obj["id"] = str(obj["_id"])
        del obj["_id"]
    return obj


# Notification Model
class Notification(BaseModel):
    user_id: str
    message: str
    is_read: bool = False
    timestamp: datetime = datetime.utcnow()

# Notification CRUD Functions
def add_notification(notification: Notification):
    notification_dict = notification.dict()
    result = notifications_collection.insert_one(notification_dict)
    return {"id": str(result.inserted_id)}

def get_notification(notification_id: str):
    notification = notifications_collection.find_one({"_id": ObjectId(notification_id)})
    return convert_id(notification) if notification else None