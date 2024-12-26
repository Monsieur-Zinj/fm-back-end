from fastapi import APIRouter, Depends, HTTPException
from .database import db
from models import Assignment, Progress
from .dependencies import get_current_teacher, get_current_user
from datetime import datetime

router = APIRouter(prefix="/assignments")

@router.post("")
async def create_assignment(
    assignment: Assignment, 
    current_user: dict = Depends(get_current_teacher)
):
    result = await db.assignments.insert_one(assignment.dict())
    return {"id": str(result.inserted_id)}

@router.get("/student")
async def get_student_assignments(current_user: dict = Depends(get_current_user)):
    assignments = await db.assignments.find(
        {"student_id": current_user["_id"]}
    ).to_list(None)
    return assignments

@router.post("/{assignment_id}/progress")
async def update_assignment_progress(
    assignment_id: str,
    progress: Progress,
    current_user: dict = Depends(get_current_user)
):
    if progress.student_id != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    progress.last_reviewed = datetime.utcnow()
    result = await db.progress.insert_one(progress.dict())
    return {"id": str(result.inserted_id)}
