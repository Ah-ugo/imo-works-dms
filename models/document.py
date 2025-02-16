# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime
# from bson import ObjectId
#
# class Comment(BaseModel):
#     user_id: str
#     content: str
#     timestamp: datetime = Field(default_factory=datetime.utcnow)
#     replies: List["Comment"] = []
#
# class DocumentBase(BaseModel):
#     title: str
#     project_id: str
#     reference_number: str
#     document_type: str  # contract, letter, approval, etc.
#     description: Optional[str] = None
#     parent_document_id: Optional[str] = None  # For document replies
#
# class DocumentCreate(DocumentBase):
#     uploaded_by: str
#     file_url: str
#
# class DocumentUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     status: Optional[str] = None
#     reference_number: Optional[str] = None
#
# class Document(DocumentBase):
#     id: str = Field(default=None, alias="_id")
#     uploaded_by: str
#     status: str = "pending"  # pending, approved, rejected
#     signed_by: List[str] = []
#     comments: List[Comment] = []
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#
#     class Config:
#         from_attributes = True
#         populate_by_name = True
#         json_encoders = {ObjectId: str}


from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Comment(BaseModel):
    user_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    replies: List["Comment"] = []

# class DocumentBase(BaseModel):
#     title: str
#     project_id: str
#     reference_number: str
#     document_type: str  # contract, letter, approval, etc.
#     file_url: Optional[str] = None
#     description: Optional[str] = None
#     parent_document_id: Optional[str] = None  # For document replies


class FileItem(BaseModel):
    url: str
    name: str

class FileItemUpdate(BaseModel):
    url: Optional[str] = None
    name: Optional[str] = None

class DocumentBase(BaseModel):
    title: str
    project_id: str
    reference_number: str
    document_type: str
    description: Optional[str] = None
    parent_document_id: Optional[str] = None

class DocumentCreate(DocumentBase):
    uploaded_by: str  # File will be handled separately

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    reference_number: Optional[str] = None
    # file_items: Optional[List[FileItemUpdate]] = None # No longer directly included here

class Document(DocumentBase):
    id: str = Field(default=None, alias="_id")
    uploaded_by: str
    status: str = "pending"
    signed_by: List[str] = []
    comments: List[Comment] = []
    file_items: List[FileItem] = [] # List of FileItems
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        populate_by_name = True
