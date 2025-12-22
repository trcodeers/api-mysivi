from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.user import User
from app.schemas.user import ReporteeCreate
from app.core.permissions import require_manager
from app.core.roles import UserRole
from app.core.security import hash_password
from app.core.config import RATE_LIMITS
from app.core.rate_limit import limiter

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/reportees")
@limiter.limit(RATE_LIMITS.create_reportee)
def create_reportee(
    request: Request,
    payload: ReporteeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_manager)
):
    # Ensure username is unique
    existing = db.query(User).filter(
        User.username == payload.username
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    reportee = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=UserRole.REPORTEE,
        company_id=current_user["company_id"],
        manager_id=int(current_user["sub"])
    )

    db.add(reportee)
    db.commit()
    db.refresh(reportee)

    return {
        "id": reportee.id,
        "username": reportee.username,
        "message": "Reportee created successfully"
    }
