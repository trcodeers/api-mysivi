from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.task import TaskCreate, TaskAssign, TaskStatusUpdate
from app.models.task import Task
from app.models.user import User
from app.core.permissions import require_manager, require_reportee, get_current_user
from app.core.task_status import TaskStatus
from app.core.rate_limit import limiter
from app.core.config import RATE_LIMITS

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# List tasks for current user (manager or reportee)
@router.get("")
@limiter.limit(RATE_LIMITS.task_list)
def list_tasks(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Manager view
    if current_user["role"] == "MANAGER":
        tasks = db.query(Task).filter(
            Task.created_by_id == int(current_user["sub"]),
            Task.company_id == current_user["company_id"],
            Task.is_deleted == False
        ).all()

    # Reportee view
    elif current_user["role"] == "REPORTEE":
        tasks = db.query(Task).filter(
            Task.assigned_to_id == int(current_user["sub"]),
            Task.company_id == current_user["company_id"],
            Task.is_deleted == False
        ).all()

    else:
        raise HTTPException(status_code=403, detail="Invalid role")

    return [
        {
            "task_id": task.id,
            "title": task.title,
            "status": task.status,
            "assigned_to_id": task.assigned_to_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
        for task in tasks
    ]


# Create a new task (optionally assigned to a reportee)
@router.post("")
@limiter.limit(RATE_LIMITS.task_create)
def create_task(
    request: Request,
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


# Assign or reassign task to reportee of the Same company
@router.patch("/{task_id}/assign")
@limiter.limit(RATE_LIMITS.task_assign)
def assign_task(
    request: Request,
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


# To delete task by manager only
@router.delete("/{task_id}")
@limiter.limit(RATE_LIMITS.task_delete)
def delete_task(
    request: Request,
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.created_by_id == int(current_user["sub"]),
        Task.company_id == current_user["company_id"],
        Task.is_deleted == False
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_deleted = True
    db.commit()

    return {
        "task_id": task.id,
        "message": "Task deleted successfully"
    }


# To update task status by manager only
@router.patch("/{task_id}/status")
@limiter.limit(RATE_LIMITS.task_status_update)
def update_task_status_by_manager(
    request: Request,
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager)
):
    # 1️⃣ Fetch task owned by this manager
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.created_by_id == int(current_user["sub"]),
        Task.company_id == current_user["company_id"],
        Task.is_deleted == False
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2️⃣ Update status (manager can set ANY status)
    task.status = payload.status
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "new_status": task.status,
        "message": "Task status updated successfully"
    }


# To update task status by reportee only
@router.patch("/{task_id}/self")
@limiter.limit(RATE_LIMITS.task_status_self_update)
def update_task_status_by_reportee(
    request: Request,
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_reportee)
):
    # 1️⃣ Fetch task assigned to this reportee
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == int(current_user["sub"]),
        Task.company_id == current_user["company_id"],
        Task.is_deleted == False
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail="Task is already completed"
        )


    # 2️⃣ BUSINESS RULE (current strategy)
    if payload.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=403,
            detail="Reportee can update task status only to COMPLETED"
        )
    
    # 3️⃣ Update status
    task.status = payload.status
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "new_status": task.status,
        "message": "Task status updated successfully"
    }
