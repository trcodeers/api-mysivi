from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.task import TaskCreate, TaskAssign
from app.models.task import Task
from app.models.user import User
from app.core.permissions import require_manager

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/")
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager)
):
    assigned_to_id = None  # default: unassigned task

    # 👉 Only validate reportee IF assigned_to_id is provided
    if payload.assigned_to_id is not None:
        reportee = db.query(User).filter(
            User.id == payload.assigned_to_id,
            User.company_id == current_user["company_id"],
            User.role == "REPORTEE"
        ).first()

        if not reportee:
            raise HTTPException(
                status_code=400,
                detail="Invalid reportee for this company"
            )

        assigned_to_id = reportee.id

    # 👉 Create task (assigned OR unassigned)
    task = Task(
        title=payload.title,
        description=payload.description,
        assigned_to_id=assigned_to_id,   # can be None
        created_by_id=int(current_user["sub"]),
        company_id=current_user["company_id"]
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "assigned_to_id": assigned_to_id,
        "message": "Task created successfully"
    }



@router.patch("/{task_id}/assign")
def assign_task(
    task_id: int,
    payload: TaskAssign,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager)
):
    # 1️⃣ Fetch task (must belong to same company)
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.company_id == current_user["company_id"],
        Task.is_deleted == False
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2️⃣ Fetch reportee (must belong to same company)
    reportee = db.query(User).filter(
        User.id == payload.assigned_to_id,
        User.company_id == current_user["company_id"],
        User.role == "REPORTEE"
    ).first()

    if not reportee:
        raise HTTPException(
            status_code=400,
            detail="Invalid reportee for this company"
        )

    # 3️⃣ Assign / reassign task
    task.assigned_to_id = reportee.id
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "assigned_to_id": reportee.id,
        "message": "Task assigned successfully"
    }