from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from jose import jwt
from .database import db
from models import Teacher, Student
import os

router = APIRouter()
ph = PasswordHasher()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.teachers.find_one({"username": form_data.username})
    if not user:
        user = await db.students.find_one({"username": form_data.username})
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    try:
        ph.verify(user["password"], form_data.password)
    except:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
