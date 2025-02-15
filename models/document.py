from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Comment(BaseModel):
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    replies: List["Comment"] = []

class DocumentBase(BaseModel):
    title: str
    project_id: str
    reference_number: str
    document_type: str  # contract, letter, approval, etc.
    description: Optional[str] = None
    parent_document_id: Optional[str] = None  # For document replies

class DocumentCreate(DocumentBase):
    uploaded_by: str
    file_url: str

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    reference_number: Optional[str] = None

class Document(DocumentBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    uploaded_by: str
    status: str = "pending"  # pending, approved, rejected
    signed_by: List[str] = []
    comments: List[Comment] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
