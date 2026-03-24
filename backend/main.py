from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Import internal modules
import crud
import models
import schemas

# Import database engine and session
from database import engine
from database import SessionLocal

# Imports for frontend integration (serving HTML, CSS, JS)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

import os


# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------
# This line creates all database tables based on models.py
# If the table does not exist → it will be created
models.Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ---------------------------------------------------------
# This initializes the FastAPI app with a custom title
app = FastAPI(title="Table Time API")


# ---------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) allows the frontend
# (HTML/JS) to communicate with the backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (NOT recommended in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# DATABASE DEPENDENCY
# ---------------------------------------------------------
# This function provides a database session to each request
# It opens a connection → yields it → then closes it automatically
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provide the DB session to the route
    finally:
        db.close()  # Ensure connection is always closed


# ---------------------------------------------------------
# ROUTE: CREATE TASK (POST)
# ---------------------------------------------------------
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # Receives validated data (TaskCreate schema)
    # Calls CRUD function to insert into DB
    return crud.create_task(db=db, task=task)


# ---------------------------------------------------------
# ROUTE: GET ALL TASKS (GET)
# ---------------------------------------------------------
@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Retrieves all tasks from DB
    # skip and limit can be used for pagination
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


# ---------------------------------------------------------
# ROUTE: GET ONE TASK BY ID (GET)
# ---------------------------------------------------------
@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    # Fetch task from DB
    db_task = crud.get_task(db, task_id=task_id)

    # If task not found → return HTTP 404 error
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task


# ---------------------------------------------------------
# ROUTE: UPDATE TASK (PUT)
# ---------------------------------------------------------
@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    # Update task using CRUD function
    db_task = crud.update_task(db, task_id=task_id, task=task)

    # If task does not exist → return 404
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task


# ---------------------------------------------------------
# ROUTE: DELETE TASK (DELETE)
# ---------------------------------------------------------
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    # Attempt to delete task
    success = crud.delete_task(db, task_id=task_id)

    # If task does not exist → return 404
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return success message
    return {"status": "success"}


# ---------------------------------------------------------
# ROOT ROUTE (HEALTH CHECK)
# ---------------------------------------------------------
@app.get("/")
def root():
    # Simple endpoint to verify that API is running
    return {"message": "Table Time API is running"}


# ---------------------------------------------------------
# FRONTEND INTEGRATION (STATIC FILES + TEMPLATES)
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
# Mount static files (CSS, JS)
# This makes files accessible at: /static/...
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")

# Configure templates directory (HTML files)
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

# ---------------------------------------------------------
# ROUTE: SERVE FRONTEND UI
# ---------------------------------------------------------
@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    # Renders index.html and sends it to the browser
    # "request" is required by Jinja2Templates
    return templates.TemplateResponse("index.html", {"request": request})