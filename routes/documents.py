from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from bson import ObjectId
from models.document import Document, DocumentCreate, DocumentUpdate, Comment
from database import documents_collection
from auth import get_current_user, get_current_admin_user
from services.cloudinary_service import cloudinary_uploader
from routes.notifications import send_notification
import re

router = APIRouter()


@router.post("/", response_model=Document)
async def create_document(
        file: UploadFile = File(...),
        title: str = Form(...),
        project_id: str = Form(...),
        reference_number: str = Form(...),
        document_type: str = Form(...),
        uploaded_by: str = Depends(get_current_user),
        description: Optional[str] = Form(None),
        parent_document_id: Optional[str] = Form(None)
):
    file_url = cloudinary_uploader.upload(file.file)
    document_data = DocumentCreate(
        title=title,
        project_id=project_id,
        reference_number=reference_number,
        document_type=document_type,
        description=description,
        uploaded_by=uploaded_by.id,
        file_url=file_url,
        parent_document_id=parent_document_id
    )
    result = await documents_collection.insert_one(document_data.dict())
    new_document = await documents_collection.find_one({"_id": result.inserted_id})
    await send_notification(f"New document uploaded: {title}")
    return Document(**new_document)


@router.post("/{document_id}/reply", response_model=Document)
async def upload_document_reply(
        document_id: str,
        file: UploadFile = File(...),
        title: str = Form(...),
        uploaded_by: str = Depends(get_current_user)
):
    file_url = cloudinary_uploader.upload(file.file)
    parent_document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not parent_document:
        raise HTTPException(status_code=404, detail="Parent document not found")

    reply_data = DocumentCreate(
        title=title,
        project_id=parent_document["project_id"],
        reference_number=parent_document["reference_number"],
        document_type=parent_document["document_type"],
        uploaded_by=uploaded_by.id,
        file_url=file_url,
        parent_document_id=document_id
    )
    result = await documents_collection.insert_one(reply_data.dict())
    new_reply = await documents_collection.find_one({"_id": result.inserted_id})
    await send_notification(f"Document reply uploaded: {title}")
    return Document(**new_reply)


@router.get("/{document_id}/replies", response_model=List[Document])
async def get_document_replies(document_id: str):
    replies = await documents_collection.find({"parent_document_id": document_id}).to_list(None)
    return [Document(**reply) for reply in replies]


@router.get("/search", response_model=List[Document])
async def search_documents(
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

    documents = await documents_collection.find(query).to_list(None)
    return [Document(**doc) for doc in documents]


@router.put("/{document_id}/comments/{comment_index}", response_model=Document)
async def edit_comment(document_id: str, comment_index: int, content: str, user=Depends(get_current_user)):
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document or len(document["comments"]) <= comment_index:
        raise HTTPException(status_code=404, detail="Comment not found")
    if document["comments"][comment_index]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    document["comments"][comment_index]["content"] = content
    await documents_collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"comments": document["comments"]}})
    return Document(**document)


@router.delete("/{document_id}/comments/{comment_index}")
async def delete_comment(document_id: str, comment_index: int, user=Depends(get_current_user)):
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document or len(document["comments"]) <= comment_index:
        raise HTTPException(status_code=404, detail="Comment not found")
    if document["comments"][comment_index]["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    document["comments"].pop(comment_index)
    await documents_collection.update_one({"_id": ObjectId(document_id)}, {"$set": {"comments": document["comments"]}})
    return JSONResponse(content={"message": "Comment deleted successfully"})


@router.get("/{document_id}/status", response_model=str)
async def get_document_status(document_id: str):
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document["status"]


@router.get("/search", response_model=List[Document])
async def search_documents(title: str):
    regex = re.compile(f".*{title}.*", re.IGNORECASE)
    documents = await documents_collection.find({"title": regex}).to_list(None)
    return [Document(**doc) for doc in documents]

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str):
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**document)

@router.put("/{document_id}", response_model=Document)
async def update_document(document_id: str, update_data: DocumentUpdate, user=Depends(get_current_admin_user)):
    await documents_collection.update_one({"_id": ObjectId(document_id)}, {"$set": update_data.dict(exclude_unset=True)})
    updated_document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    return Document(**updated_document)

@router.delete("/{document_id}")
async def delete_document(document_id: str, user=Depends(get_current_admin_user)):
    result = await documents_collection.delete_one({"_id": ObjectId(document_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return JSONResponse(content={"message": "Document deleted successfully"})

@router.post("/{document_id}/comments", response_model=Document)
async def add_comment(document_id: str, content: str, user=Depends(get_current_user)):
    comment = Comment(user_id=user.id, content=content)
    await documents_collection.update_one({"_id": ObjectId(document_id)}, {"$push": {"comments": comment.dict()}})
    updated_document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    return Document(**updated_document)

@router.get("/{document_id}/comments", response_model=List[Comment])
async def get_document_comments(document_id: str):
    document = await documents_collection.find_one({"_id": ObjectId(document_id)})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.get("comments", [])
