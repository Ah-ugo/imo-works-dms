from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from bson import ObjectId
from database import users_collection
from models.user import User, UserCreate, UserUpdate, UserInDB
from services.auth import get_current_user, get_current_admin_user, get_password_hash
from services.cloudinary_service import cloudinary_uploader
from pymongo import ReturnDocument
import datetime

router = APIRouter()


# Get all users (Admin only)
@router.get("/", response_model=List[User])
async def get_users(current_admin: User = Depends(get_current_admin_user)):
    users = await users_collection.find().to_list(None)
    return [User(**user) for user in users]


# Get user by ID (Admin only)
@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, current_admin: User = Depends(get_current_admin_user)):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)


# Create a new user (Admin only)
@router.post("/", response_model=User)
async def create_user(user_data: UserCreate, current_admin: User = Depends(get_current_admin_user)):
    if await users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict(exclude={"password"})
    user_dict["password_hash"] = hashed_password
    user_dict["created_at"] = user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True

    new_user = await users_collection.insert_one(user_dict)
    user_dict["id"] = str(new_user.inserted_id)

    return User(**user_dict)


# Update user details (Admin can update any user, user can update their own profile)
@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: UserUpdate, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = {k: v for k, v in user_data.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    updated_user = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return User(**updated_user)


# Upload profile image
@router.post("/{user_id}/upload-profile", response_model=User)
async def upload_profile_image(user_id: str, file: UploadFile = File(...),
                               current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
        image_url = cloudinary_uploader.upload(file.file, folder="users")
        updated_user = await users_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_image": image_url, "updated_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER
        )
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**updated_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete user (Admin only)
@router.delete("/{user_id}")
async def delete_user(user_id: str, current_admin: User = Depends(get_current_admin_user)):
    deleted_user = await users_collection.find_one_and_delete({"_id": ObjectId(user_id)})
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
