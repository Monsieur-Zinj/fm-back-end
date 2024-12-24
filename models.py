from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

class Teacher(BaseModel):
    _id: str
    username: str
    email: EmailStr
    password: str

class Student(BaseModel):
    _id: str
    username: str
    email: EmailStr
    password: str

class TeacherStudent(BaseModel):
    _id: str
    teacher_id: str
    student_id: str
    relation_date: datetime

class ClassGroup(BaseModel):
    _id: str
    name: str
    teacher_id: str
    year: int

class ClassGroupStudent(BaseModel):
    _id: str
    classgroup_id: str
    student_id: str

class Deck(BaseModel):
    _id: str
    name: str
    description: str
    created_by: str
    is_public: bool
    cloned_from: Optional[str] = None

class CardOption(BaseModel):
    text: str
    is_correct: bool

class Card(BaseModel):
    _id: str
    deck_id: str
    question: str
    options: List[CardOption]

class Assignment(BaseModel):
    _id: str
    deck_id: str
    student_id: str
    assigned_date: datetime

class Progress(BaseModel):
    _id: str
    student_id: str
    card_id: str
    last_reviewed: datetime
    review_count: int
    ease_factor: float
    next_review_date: datetime
