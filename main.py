from fastapi import FastAPI
from routeurs import auth, teachers, decks, assignments, students

app = FastAPI()

# Include your routers
app.include_router(auth.router)
app.include_router(teachers.router)
app.include_router(decks.router)
app.include_router(assignments.router)
app.include_router(students.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Flashcard App API"}
