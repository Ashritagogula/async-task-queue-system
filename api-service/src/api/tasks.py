import uuid
from typing import Optional, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.models.task import Task
from src.services.rabbitmq import publish_task

router = APIRouter(prefix="/api")


# =========================
# Request Schema
# =========================
class TaskCreate(BaseModel):
    title: str
    description: str
    metadata: Optional[Dict] = None


# =========================
# Response Schema
# =========================
class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: str
    status: str
    metadata: Optional[Dict]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True   # ✅ REQUIRED for SQLAlchemy objects


# =========================
# POST /api/tasks
# =========================
@router.post("/tasks", status_code=status.HTTP_202_ACCEPTED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    if not task.title.strip() or not task.description.strip():
        raise HTTPException(
            status_code=400,
            detail="Title and description must not be empty"
        )

    task_id = str(uuid.uuid4())

    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        task_metadata=task.metadata,   # ✅ NOT `metadata`
        status="PENDING"
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Send message to RabbitMQ
    publish_task({
        "task_id": task_id
    })

    return {
        "task_id": task_id,
        "message": "Task submitted successfully"
    }


# =========================
# GET /api/tasks/{task_id}
# =========================
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        task_id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        metadata=task.task_metadata,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )

