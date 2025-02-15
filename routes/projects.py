from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, File
from bson import ObjectId
from datetime import datetime
from database import projects_collection
from models.project import Project
from services.auth import get_current_user, get_current_admin_user
from typing import List, Optional
from services.cloudinary_service import cloudinary_uploader

router = APIRouter()

@router.post("/", response_model=Project)
async def create_project(
    project_name: str = Form(...),
    description: Optional[str] = Form(None),
    # file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Create a new project with file upload."""
    # file_url = cloudinary_uploader.upload(file.file)
    project_dict = {
        "project_name": project_name,
        "description": description,
        # "file_url": file_url,
        "created_by": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await projects_collection.insert_one(project_dict)
    project_dict["id"] = str(result.inserted_id)
    return Project(**project_dict)

@router.get("/", response_model=List[Project])
async def get_projects():
    """Retrieve all projects sorted by creation date."""
    projects = await projects_collection.find().sort("created_at", -1).to_list(None)
    return [Project(**project, id=str(project["_id"])) for project in projects]

@router.get("/id/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str):
    """Retrieve a project by its ID."""
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project, id=str(project["_id"]))

@router.get("/name/{project_name}", response_model=List[Project])
async def get_project_by_name(project_name: str):
    """Retrieve projects by name."""
    projects = await projects_collection.find({"project_name": project_name}).to_list(None)
    if not projects:
        raise HTTPException(status_code=404, detail="No projects found with this name")
    return [Project(**project, id=str(project["_id"])) for project in projects]

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    # file: Optional[UploadFile] = File(None),
    current_user=Depends(get_current_user)
):
    """Update a project with optional file upload."""
    update_data = {}
    if project_name:
        update_data["project_name"] = project_name
    if description:
        update_data["description"] = description
    # if file:
    #     file_url = cloudinary_uploader.upload(file.file)
    #     update_data["file_url"] = file_url
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await projects_collection.update_one({"_id": ObjectId(project_id)}, {"$set": update_data})
    updated_project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**updated_project, id=str(updated_project["_id"]))

@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: str, current_user=Depends(get_current_admin_user)):
    """Delete a project (Admin only)."""
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # if "file_url" in project:
    #     cloudinary_uploader.delete(project["file_url"].split("/")[-1].split(".")[0])
    await projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"message": "Project deleted successfully"}
