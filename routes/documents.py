from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from bson import ObjectId
from models.document import Document, DocumentCreate, DocumentUpdate, Comment, FileItemUpdate, FileItem
from database import documents_collection
from services.auth import get_current_user, get_current_admin_user
from services.cloudinary_service import cloudinary_uploader
from routes.notifications import send_notification
from datetime import datetime

router = APIRouter()


parent_id = "67b0d24045ee190e437238e0"  # Parent document ID from the request
document = documents_collection.find_one({"_id": ObjectId(parent_id)})

if document:
    print("Document exists:", document)
else:
    print("Parent document not found!")

# @router.post("/", response_model=Document)
# def create_document(
#         file: UploadFile = File(...),
#         title: str = Form(...),
#         project_id: str = Form(...),
#         reference_number: str = Form(...),
#         document_type: str = Form(...),
#         uploaded_by: str = Depends(get_current_user),
#         description: Optional[str] = Form(None),
#         parent_document_id: Optional[str] = Form(None)
# ):
#     file_url = cloudinary_uploader.upload(file.file)
#     document_data = DocumentCreate(
#         title=title,
#         project_id=project_id,
#         reference_number=reference_number,
#         document_type=document_type,
#         description=description,
#         uploaded_by=uploaded_by.id,
#         file_url=file_url,
#         parent_document_id=parent_document_id
#     )
#     # Convert Pydantic model to dictionary and insert into MongoDB
#     document_dict = document_data.dict()
#     result = documents_collection.insert_one(document_dict)
#
#     # Update the dictionary with the inserted ID
#     document_dict["id"] = str(result.inserted_id)
#
#     new_document = documents_collection.find_one({"_id": result.inserted_id})
#     return Document(**new_document)


# @router.post("/", response_model=Document)
# async def create_document(
#     file: UploadFile = File(...),
#     title: str = Form(...),
#     project_id: str = Form(...),
#     reference_number: str = Form(...),
#     document_type: str = Form(...),
#     uploaded_by: str = Depends(get_current_user),
#     description: Optional[str] = Form(None),
#     parent_document_id: Optional[str] = Form(None)
# ):
#     """Uploads a file to Cloudinary and saves the document data in MongoDB."""
#
#     # Upload file to Cloudinary
#     # upload_result = cloudinary_uploader.upload(file.file)
#     file_url = cloudinary_uploader.upload(file.file)
#
#     # Prepare document data
#     document_data = {
#         "title": title,
#         "project_id": project_id,
#         "reference_number": reference_number,
#         "document_type": document_type,
#         "description": description,
#         "uploaded_by": uploaded_by.id if hasattr(uploaded_by, "id") else uploaded_by,
#         "file_url": file_url,
#         "parent_document_id": parent_document_id,
#         "status": "pending",
#         "signed_by": [],
#         "comments": [],
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }
#
#     # Insert into MongoDB
#     result = documents_collection.insert_one(document_data)
#
#     # Fetch the newly inserted document
#     new_document = documents_collection.find_one({"_id": result.inserted_id})
#
#     # Convert _id to string before returning
#     new_document["id"] = str(new_document.pop("_id"))
#
#     return Document(**new_document)


@router.post("/", response_model=Document)
async def create_document(
    files: List[UploadFile] = File(...),  # Accept multiple files
    title: str = Form(...),
    project_id: str = Form(...),
    reference_number: str = Form(...),
    document_type: str = Form(...),
    uploaded_by: str = Depends(get_current_user),
    description: Optional[str] = Form(None),
    parent_document_id: Optional[str] = Form(None)
):
    """Uploads multiple files to Cloudinary and saves the document data in MongoDB."""

    file_items = []
    for file in files:
        file_url = cloudinary_uploader.upload(file.file)
        file_items.append(FileItem(url=file_url, name=file.filename))  # Store file details

    document_data = {
        "title": title,
        "project_id": project_id,
        "reference_number": reference_number,
        "document_type": document_type,
        "description": description,
        "uploaded_by": uploaded_by.id if hasattr(uploaded_by, "id") else uploaded_by,
        "file_items": [item.dict() for item in file_items],  # Store list of file items
        "parent_document_id": parent_document_id,
        "status": "pending",
        "signed_by": [],
        "comments": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = documents_collection.insert_one(document_data)
    new_document = documents_collection.find_one({"_id": result.inserted_id})
    new_document["id"] = str(new_document.pop("_id"))
    return Document(**new_document)





@router.post("/{document_id}/reply", response_model=Document)
async def upload_document_reply(
    document_id: str,
    files: List[UploadFile] = File(...),  # Accept multiple files
    title: str = Form(...),
    uploaded_by: str = Depends(get_current_user)
):
    parent_document = documents_collection.find_one({"_id": ObjectId(document_id)})
    if not parent_document:
        raise HTTPException(status_code=404, detail="Parent document not found")

    file_items = []
    for file in files:
        file_url = cloudinary_uploader.upload(file.file)
        file_items.append(FileItem(url=file_url, name=file.filename))

    reply_data = {  # Use a dictionary directly
        "title": title,
        "project_id": parent_document["project_id"],
        "reference_number": parent_document["reference_number"],
        "document_type": parent_document["document_type"],
        "uploaded_by": uploaded_by.id,
        "file_items": [item.dict() for item in file_items],  # Store list of file items
        "parent_document_id": document_id,  # Important: Use the parent document ID
        "status": "pending",
        "signed_by": [],
        "comments": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = documents_collection.insert_one(reply_data)
    new_reply = documents_collection.find_one({"_id": result.inserted_id})
    new_reply["id"] = str(new_reply.pop("_id"))  # Convert _id to string
    return Document(**new_reply)

@router.get("/{document_id}/replies", response_model=List[Document])
def get_document_replies(document_id: str):
    replies = documents_collection.find({"parent_document_id": document_id})
    return [Document(**{**reply, "_id": str(reply["_id"])}) for reply in replies]


@router.get("/search", response_model=List[Document])
def search_documents(
        title: Optional[str] = None,
        project_id: Optional[str] = None,
        reference_number: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[str] = None
):
    query = {}
    if title:
        query["title"] = {"$regex": f".*{title}.*", "$options": "i"}
    if project_id:
        query["project_id"] = project_id
    if reference_number:
        query["reference_number"] = reference_number
    if document_type:
        query["document_type"] = document_type
    if status:
        query["status"] = status

    documents = documents_collection.find(query)

    return [Document(**{**doc, "_id": str(doc["_id"])}) for doc in documents]




@router.put("/{document_id}/files/{file_index}", response_model=Document)
async def update_document_file(
    document_id: str,
    file_index: int,
    file: UploadFile = File(...),
    user=Depends(get_current_admin_user)
):
    """Updates a specific file within a document."""

    document = documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document or len(document["file_items"]) <= file_index:
        raise HTTPException(status_code=404, detail="File not found")

    file_url = cloudinary_uploader.upload(file.file)
    document["file_items"][file_index]["url"] = file_url  # Update the URL
    document["file_items"][file_index]["name"] = file.filename # Update the name

    documents_collection.update_one(
        {"_id": ObjectId(document_id)}, {"$set": {"file_items": document["file_items"]}}
    )
    updated_document = documents_collection.find_one({"_id": ObjectId(document_id)})
    updated_document["id"] = str(updated_document.pop("_id"))
    return Document(**updated_document)




@router.put("/{document_id}", response_model=Document)
def update_document(document_id: str, update_data: DocumentUpdate, user=Depends(get_current_admin_user)):
    # Exclude file_items from the main update, handle them separately
    update_data_dict = update_data.dict(exclude_unset=True)
    if update_data_dict:  # Check if there are other fields to update
        documents_collection.update_one({"_id": ObjectId(document_id)}, {"$set": update_data_dict})

    updated_document = documents_collection.find_one({"_id": ObjectId(document_id)})
    updated_document["id"] = str(updated_document.pop("_id"))
    return Document(**updated_document)


@router.put("/{document_id}/comments/{comment_index}", response_model=Document)
def edit_comment(document_id: str, comment_index: int, content: str, user=Depends(get_current_user)):
    document = documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document or len(document["comments"]) <= comment_index:
        raise HTTPException(status_code=404, detail="Comment not found")
    if document["comments"][comment_index]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    document["comments"][comment_index]["content"] = content
    documents_collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"comments": document["comments"]}})
    return Document(**document)


@router.delete("/{document_id}/comments/{comment_index}")
def delete_comment(document_id: str, comment_index: int, user=Depends(get_current_user)):
    document = documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document or len(document["comments"]) <= comment_index:
        raise HTTPException(status_code=404, detail="Comment not found")
    if document["comments"][comment_index]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    document["comments"].pop(comment_index)
    documents_collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"comments": document["comments"]}})
    return JSONResponse(content={"message": "Comment deleted successfully"})


@router.get("/{document_id}/status", response_model=str)
def get_document_status(document_id: str):
    document = documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document["status"]


@router.get("/search", response_model=List[Document])
def search_documents(title: str):
    regex = re.compile(f".*{title}.*", re.IGNORECASE)
    documents = documents_collection.find({"title": regex}).to_list(None)
    return [Document(**doc) for doc in documents]

@router.get("/{document_id}", response_model=Document)
def get_document(document_id: str):
    document = documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document["_id"] = str(document["_id"])  # Explicitly map `_id` to `id`
    return Document(**document)


@router.put("/{document_id}", response_model=Document)
def update_document(document_id: str, update_data: DocumentUpdate, user=Depends(get_current_admin_user)):
    documents_collection.update_one({"_id": ObjectId(document_id)}, {"$set": update_data.dict(exclude_unset=True)})
    updated_document = documents_collection.find_one({"_id": ObjectId(document_id)})
    return Document(**updated_document)

@router.delete("/{document_id}")
def delete_document(document_id: str, user=Depends(get_current_admin_user)):
    result = documents_collection.delete_one({"_id": ObjectId(document_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return JSONResponse(content={"message": "Document deleted successfully"})

@router.post("/{document_id}/comments", response_model=Document)
def add_comment(document_id: str, content: str, user=Depends(get_current_user)):
    comment = Comment(user_id=user.id, content=content)
    documents_collection.update_one({"_id": ObjectId(document_id)}, {"$push": {"comments": comment.dict()}})
    updated_document = documents_collection.find_one({"_id": ObjectId(document_id)})
    return Document(**updated_document)

@router.get("/{document_id}/comments", response_model=List[Comment])
def get_document_comments(document_id: str):
    document = documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.get("comments", [])
