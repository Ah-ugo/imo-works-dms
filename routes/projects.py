from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, File
from bson import ObjectId
from datetime import datetime
from database import projects_collection, documents_collection
from models.document import Document
from models.project import Project
from services.auth import get_current_user, get_current_admin_user
from typing import List, Optional
from services.cloudinary_service import cloudinary_uploader

router = APIRouter()

@router.post("/", response_model=Project)
def create_project(
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
    result = projects_collection.insert_one(project_dict)
    project_dict["id"] = str(result.inserted_id)
    return Project(**project_dict)

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
        {"project_name": {"$regex": project_name, "$options": "i"}}  # Case-insensitive regex search
    )

    projects_list = list(projects)  # Convert cursor to list

    if not projects_list:
        raise HTTPException(status_code=404, detail="No projects found with this name")

    return [
        Project(**{**project, "id": str(project["_id"])}) for project in projects_list
    ]



@router.get("/recent", response_model=List[Project])
def get_recent_projects(limit: int = 5, user=Depends(get_current_user)):  # Add limit parameter
    """Retrieves the most recently uploaded documents."""

    projects = list(projects_collection.find().sort([("created_at", -1)]).limit(limit))

    # Convert ObjectIds to strings and return as Document objects
    recent_projects = []
    for proj in projects:
        proj["id"] = str(proj.pop("_id")) # Move and convert _id to id
        recent_projects.append(Project(**proj))
    return recent_projects



@router.get("/{project_id}/documents", response_model=List[Document])
def get_project_documents(project_id: str):
    """Retrieve all documents associated with a specific project."""
    try:
        documents = list(documents_collection.find({"project_id": project_id})) # Convert cursor to list immediately

        project_documents = []
        for doc in documents:
            doc["id"] = str(doc.pop("_id"))  # Convert ObjectId to string and assign to "id"
            project_documents.append(Document(**doc))

        return project_documents

    except Exception as e:
        import logging
        logging.error(f"Error getting project documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")




@router.put("/{project_id}", response_model=Project)
def update_project(
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
        projects_collection.update_one({"_id": ObjectId(project_id)}, {"$set": update_data})
    updated_project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**updated_project, id=str(updated_project["_id"]))

@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str, current_user=Depends(get_current_admin_user)):
    """Delete a project (Admin only)."""
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # if "file_url" in project:
    #     cloudinary_uploader.delete(project["file_url"].split("/")[-1].split(".")[0])
    projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"message": "Project deleted successfully"}
