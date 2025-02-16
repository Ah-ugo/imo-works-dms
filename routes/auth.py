from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from database import users_collection
from models.user import User, UserInDB
from bson import ObjectId
from config import settings
from services.cloudinary_service import cloudinary_uploader

router = APIRouter()

# Security settings
SECRET_KEY = "settings.SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(email: str, password: str):
    user = users_collection.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return UserInDB(**user, id=str(user["_id"]))


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.email, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
def register_user(
        email: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        password: str = Form(...),
        profile_image: Optional[UploadFile] = File(None)
):
    """Register a new user."""
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    hashed_password = get_password_hash(password)
    profile_image_url = None
    if profile_image:
        profile_image_url = cloudinary_uploader.upload(profile_image.file)

    user_dict = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password_hash": hashed_password,
        "profile_image": profile_image_url,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = users_collection.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return User(**user_dict)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Retrieve the currently authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("id")
        if not email or not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise credentials_exception

    return User(**user, id=str(user["_id"]))


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is an admin."""
    if current_user.role not in ["admin", "commissioner"]:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get details of the currently logged-in user."""
    return current_user
