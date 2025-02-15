from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from fastapi_pagination import Page, add_pagination, paginate

from config import settings
from database import get_database
from models.user import User, UserCreate, UserUpdate, UserInDB
from models.project import Project, ProjectCreate, ProjectUpdate
from models.document import Document, DocumentCreate, DocumentUpdate
from models.approval import Approval, ApprovalCreate
from models.signature import Signature, SignatureCreate
from services.auth import (
    get_current_user,
    get_current_active_user,
    authenticate_user,
    create_access_token,
)
from services.cloudinary_service import cloudinary_uploader
from routers import users, projects, documents, approvals, signatures

app = FastAPI(
    title="Ministry of Works DMS",
    description="Document Management System for the Ministry of Works",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
app.include_router(signatures.router, prefix="/api/signatures", tags=["signatures"])

# Add pagination support
add_pagination(app)


@app.get("/")
async def root():
    return {"message": "Ministry of Works Document Management System API"}


@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)