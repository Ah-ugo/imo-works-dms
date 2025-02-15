from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class SignatureBase(BaseModel):
    document_id: str

class SignatureCreate(SignatureBase):
    user_id: str

class Signature(SignatureBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    signature_url: str
    signed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True