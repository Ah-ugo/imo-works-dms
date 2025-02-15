from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class ApprovalBase(BaseModel):
    document_id: str
    status: str  # approved, rejected
    reason: Optional[str] = None

class ApprovalCreate(ApprovalBase):
    approved_by: str

class Approval(ApprovalBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    approved_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True