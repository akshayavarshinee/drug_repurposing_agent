from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth.routes import get_current_user
from app.users.models import User

router = APIRouter()

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile information.
    """
    return current_user
