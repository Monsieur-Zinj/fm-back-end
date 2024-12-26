from fastapi import APIRouter, Depends
from argon2 import PasswordHasher
from .database import db
from models import Student
from .dependencies import get_current_student

router = APIRouter(prefix="/students")
ph = PasswordHasher()

@router.post("")
async def create_student(student: Student):
    student.password = ph.hash(student.password)
    result = await db.students.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

@router.get("/teachers")
async def get_student_teachers(current_user: dict = Depends(get_current_student)):
    teachers = await db.teacher_student.find(
        {"student_id": current_user["_id"]}
    ).to_list(None)
    return teachers

@router.get("/class-groups")
async def get_student_classes(current_user: dict = Depends(get_current_student)):
    classes = await db.classgroups_student.find(
        {"student_id": current_user["_id"]}
    ).to_list(None)
    return classes

@router.get("/assignments")
async def get_student_assignments(current_user: dict = Depends(get_current_student)):
    assignments = await db.assignments.find(
        {"student_id": current_user["_id"]}
    ).to_list(None)
    return assignments

@router.get("/progress")
async def get_student_progress(current_user: dict = Depends(get_current_student)):
    progress = await db.progress.find(
        {"student_id": current_user["_id"]}
    ).to_list(None)
    return progress
