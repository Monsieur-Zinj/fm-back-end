from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from jose import JWTError, jwt
from argon2 import PasswordHasher
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models import *

# Chargement variables d'environnement
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

# Configuration Auth
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup FastAPI
app = FastAPI()
ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URI)
db = client.flashcards_db

# Auth functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

# Auth routes
@app.post("/token")
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

# Teacher routes
@app.post("/teachers")
async def create_teacher(teacher: Teacher):
    teacher.password = ph.hash(teacher.password)
    result = await db.teachers.insert_one(teacher.dict())
    return {"id": str(result.inserted_id)}

@app.get("/teachers/students")
async def get_teacher_students(current_user: dict = Depends(get_current_user)):
    if not await db.teachers.find_one({"_id": current_user["_id"]}):
        raise HTTPException(status_code=403, detail="Not a teacher")
    students = await db.teacher_students.find({"teacher_id": current_user["_id"]}).to_list(None)
    return students

# Deck routes
@app.post("/decks")
async def create_deck(deck: Deck, current_user: dict = Depends(get_current_user)):
    deck.created_by = current_user["_id"]
    result = await db.decks.insert_one(deck.dict())
    return {"id": str(result.inserted_id)}

@app.get("/decks")
async def get_decks(current_user: dict = Depends(get_current_user)):
    decks = await db.decks.find({
        "$or": [
            {"created_by": current_user["_id"]},
            {"is_public": True}
        ]
    }).to_list(None)
    return decks

# Assignment routes
@app.post("/assignments")
async def create_assignment(assignment: Assignment, current_user: dict = Depends(get_current_user)):
    if not await db.teachers.find_one({"_id": current_user["_id"]}):
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.assignments.insert_one(assignment.dict())
    return {"id": str(result.inserted_id)}

@app.get("/assignments/student")
async def get_student_assignments(current_user: dict = Depends(get_current_user)):
    assignments = await db.assignments.find({"student_id": current_user["_id"]}).to_list(None)
    return assignments

# Progress routes
@app.post("/progress")
async def update_progress(progress: Progress, current_user: dict = Depends(get_current_user)):
    if progress.student_id != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.progress.insert_one(progress.dict())
    return {"id": str(result.inserted_id)}
