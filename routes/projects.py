from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, File
from bson import ObjectId
from datetime import datetime
from database import projects_collection, documents_collection
from models.document import Document
from models.project import Project
from services.auth import get_current_user, get_current_admin_user
from typing import List, Optional
from services.cloudinary_service import cloudinary_uploader
import pandas as pd
import io

def get_project_or_404(project_id: str):
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

router = APIRouter()


@router.post("/", response_model=Project)
def create_project(
        project_name: str = Form(...),
        description: Optional[str] = Form(None),
        contractor: Optional[str] = Form(None),
        resident_engineer: Optional[str] = Form(None),
        progress_report: Optional[str] = Form(None),
        project_tags: Optional[str] = Form(None),
        award_date: Optional[str] = Form(None),
        contract_sum: Optional[float] = Form(None),
        duration: Optional[str] = Form(None),
        mobilisation_paid: Optional[float] = Form(None),
        interim_certificate_earned: Optional[float] = Form(None),
        remark: Optional[str] = Form(None),
        current_user=Depends(get_current_user)
):
    """Create a new project."""
    try:
        project_dict = {
            "project_name": project_name,
            "description": description,
            "contractor": contractor,
            "resident_engineer": resident_engineer,
            "progress_report": progress_report,
            "project_tags": project_tags,
            "award_date": award_date,
            "contract_sum": contract_sum,
            "duration": duration,
            "mobilisation_paid": mobilisation_paid,
            "interim_certificate_earned": interim_certificate_earned,
            "remark": remark,
            "created_by": current_user.id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = projects_collection.insert_one(project_dict)
        project_dict["id"] = str(result.inserted_id)
        return Project(**project_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.get("/export", response_model=dict)
def export_projects():
    """Generate spreadsheet and upload to Cloudinary."""
    projects = list(projects_collection.find())
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found")

    project_data = [{
        "Title": proj["project_name"],
        "Contractor": proj.get("contractor"),
        "Resident Engineer": proj.get("resident_engineer"),
        "Progress Report": proj.get("progress_report"),
        "Project Tags": proj.get("project_tags"),
        "Award Date": proj.get("award_date"),
        "Contract Sum": proj.get("contract_sum"),
        "Duration": proj.get("duration"),
        "Mobilisation Paid": proj.get("mobilisation_paid"),
        "Interim Certificate Earned": proj.get("interim_certificate_earned"),
        "Remark": proj.get("remark"),
    } for proj in projects]

    df = pd.DataFrame(project_data)
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")  # Ensure format compatibility
    output.seek(0)

    # Create an UploadFile-like object
    output_file = UploadFile(filename="projects_export.xlsx", file=output)

    upload_result = cloudinary_uploader.upload(output_file.file, folder="project_exports")

    return {"spreadsheet_url": upload_result}


@router.get("/export/ongoing", response_model=dict)
def export_ongoing_projects():
    """Generate spreadsheet of ongoing projects and upload to Cloudinary."""
    projects = list(projects_collection.find({"project_tags": "ongoing"}))
    if not projects:
        raise HTTPException(status_code=404, detail="No ongoing projects found")

    project_data = [{
        "Title": proj["project_name"],
        "Contractor": proj.get("contractor"),
        "Resident Engineer": proj.get("resident_engineer"),
        "Progress Report": proj.get("progress_report"),
    } for proj in projects]

    df = pd.DataFrame(project_data)
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")  # Ensure format compatibility
    output.seek(0)

    # Create an UploadFile-like object
    output_file = UploadFile(filename="ongoing_projects_export.xlsx", file=output)

    upload_result = cloudinary_uploader.upload(output_file.file, folder="project_exports")

    return {"spreadsheet_url": upload_result}


@router.get("/", response_model=List[Project])
def get_projects():
    """Retrieve all projects sorted by creation date."""
    projects = projects_collection.find().sort("created_at", -1)
    return [
        Project(**{**project, "id": str(project["_id"])} if "_id" in project else project)
        for project in projects
    ]


@router.get("/id/{project_id}", response_model=Project)
def get_project_by_id(project_id: str):
    """Retrieve a project by its ID."""
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project, id=str(project["_id"]))


@router.get("/name/{project_name}", response_model=List[Project])
def get_project_by_name(project_name: str):
    """Retrieve projects by name using regex matching."""
    projects = projects_collection.find(
        {"project_name": {"$regex": project_name, "$options": "i"}}
    )
    projects_list = list(projects)
    if not projects_list:
        raise HTTPException(status_code=404, detail="No projects found with this name")
    return [
        Project(**{**project, "id": str(project["_id"])} if "_id" in project else project)
        for project in projects_list
    ]


@router.get("/recent", response_model=List[Project])
def get_recent_projects(limit: int = 5, user=Depends(get_current_user)):
    """Retrieve the most recently uploaded projects."""
    projects = list(projects_collection.find().sort([("created_at", -1)]).limit(limit))
    return [Project(**{**proj, "id": str(proj.pop("_id"))}) for proj in projects]


@router.get("/{project_id}/documents", response_model=List[Document])
def get_project_documents(project_id: str):
    """Retrieve all documents associated with a specific project."""
    documents = list(documents_collection.find({"project_id": project_id}))
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for this project")
    return [Document(**{**doc, "id": str(doc["_id"]), "_id": str(doc["_id"])}) for doc in documents]


@router.put("/projects/{project_id}")
def update_project(
        project_id: str,
        project_name: Optional[str] = None,
        contractor: Optional[str] = None,
        resident_engineer: Optional[str] = None,
        progress_report: Optional[str] = None,
        project_tags: Optional[str] = None,
        award_date: Optional[str] = None,
        contract_sum: Optional[float] = None,
        duration: Optional[str] = None,
        mobilisation_paid: Optional[float] = None,
        interim_certificate_earned: Optional[float] = None,
        remark: Optional[str] = None,
        current_user: dict = Depends(get_current_user),
):
    project = get_project_or_404(project_id)

    update_data = {}
    if project_name is not None:
        update_data["project_name"] = project_name
    if contractor is not None:
        update_data["contractor"] = contractor
    if resident_engineer is not None:
        update_data["resident_engineer"] = resident_engineer
    if progress_report is not None:
        update_data["progress_report"] = progress_report
    if project_tags is not None:
        update_data["project_tags"] = project_tags
    if award_date is not None:
        update_data["award_date"] = award_date
    if contract_sum is not None:
        update_data["contract_sum"] = contract_sum
    if duration is not None:
        update_data["duration"] = duration
    if mobilisation_paid is not None:
        update_data["mobilisation_paid"] = mobilisation_paid
    if interim_certificate_earned is not None:
        update_data["interim_certificate_earned"] = interim_certificate_earned
    if remark is not None:
        update_data["remark"] = remark

    update_data["updated_at"] = datetime.utcnow()

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    projects_collection.update_one({"_id": ObjectId(project_id)}, {"$set": update_data})

    return {"message": "Project updated successfully", "updated_fields": update_data}


@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str, current_user=Depends(get_current_admin_user)):
    """Delete a project (Admin only)."""
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if "file_url" in project:
        try:
            cloudinary_uploader.delete(project["file_url"].split("/")[-1].split(".")[0])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

    projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"message": "Project deleted successfully"}
