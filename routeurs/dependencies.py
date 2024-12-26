from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .database import db
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await db.teachers.find_one({"username": username})
    if not user:
        user = await db.students.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

async def get_current_teacher(current_user: dict = Depends(get_current_user)):
    if not await db.teachers.find_one({"_id": current_user["_id"]}):
        raise HTTPException(status_code=403, detail="Not a teacher")
    return current_user

async def get_current_student(current_user: dict = Depends(get_current_user)):
    if not await db.students.find_one({"_id": current_user["_id"]}):
        raise HTTPException(status_code=403, detail="Not a student")
    return current_user