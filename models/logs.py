from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from database import logs_collection


def convert_id(obj):
    if "_id" in obj:
        obj["id"] = str(obj["_id"])
        del obj["_id"]
    return obj


# Log Model
class Log(BaseModel):
    user_id: str
    action: str
    document_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

# Log CRUD Functions
def add_log(log: Log):
    log_dict = log.dict()
    result = logs_collection.insert_one(log_dict)
    return {"id": str(result.inserted_id)}

def get_log(log_id: str):
    log = logs_collection.find_one({"_id": ObjectId(log_id)})
    return convert_id(log) if log else None