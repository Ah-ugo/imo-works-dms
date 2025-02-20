from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class ProjectBase(BaseModel):
    project_name: str
    contractor: Optional[str] = None
    resident_engineer: Optional[str] = None
    progress_report: Optional[str] = None
    project_tags: Optional[str] = None
    award_date: Optional[str] = None
    contract_sum: Optional[float] = None
    duration: Optional[str] = None
    mobilisation_paid: Optional[float] = None
    interim_certificate_earned: Optional[float] = None
    remark: Optional[str] = None

class ProjectCreate(ProjectBase):
    created_by: str

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    contractor: Optional[str] = None
    resident_engineer: Optional[str] = None
    progress_report: Optional[str] = None
    project_tags: Optional[str] = None
    award_date: Optional[str] = None
    contract_sum: Optional[float] = None
    duration: Optional[str] = None
    mobilisation_paid: Optional[float] = None
    interim_certificate_earned: Optional[float] = None
    remark: Optional[str] = None

class Project(ProjectBase):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
