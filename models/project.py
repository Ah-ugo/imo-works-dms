from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class ProgressOfWork(BaseModel):
    road_section: Optional[str] = None
    building_section: Optional[str] = None
    structural_works: Optional[str] = None
    mse_walls: Optional[str] = None
    drainage_works: Optional[str] = None
    current_status: Optional[str] = None
    dual_section: Optional[str] = None
    single_section: Optional[str] = None
    other_progress: Optional[str] = None
    progress_summary: Optional[str] = None
    updated_at: Optional[str] = None

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

# class Project(ProjectBase):
#     id: str = Field(default_factory=lambda: str(ObjectId()))
#     created_by: str
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#
#     class Config:
#         from_attributes = True


class Project(BaseModel):
    id: Optional[str] = None
    project_name: str
    description: Optional[str] = None
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
    progress_of_work: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class ProgressEntry(BaseModel):
    progress: Dict[str, str]
