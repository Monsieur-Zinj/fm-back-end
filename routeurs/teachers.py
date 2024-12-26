from fastapi import APIRouter, Depends
from argon2 import PasswordHasher
from .database import db
from models import Teacher
from .dependencies import get_current_teacher

router = APIRouter(prefix="/teachers")
ph = PasswordHasher()

@router.post("")
async def create_teacher(teacher: Teacher):
    teacher.password = ph.hash(teacher.password)
    result = await db.teachers.insert_one(teacher.dict())
    return {"id": str(result.inserted_id)}

@router.get("/students")
async def get_teacher_students(current_user: dict = Depends(get_current_teacher)):
    print(current_user)
    students = await db.teacher_student.find(
        {"teacher_id": current_user["_id"]}
    ).to_list(None)
    print(students)
    return students

@router.get("/class-groups")
async def get_teacher_classes(current_user: dict = Depends(get_current_teacher)):
    classes = await db.classgroups.find(
        {"teacher_id": current_user["_id"]}
    ).to_list(None)
    return classes
