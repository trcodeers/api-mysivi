from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.user import User
from app.models.company import Company
from app.schemas.auth import ManagerSignup, LoginRequest
from app.core.roles import UserRole
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token
from app.core.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup")
def manager_signup(payload: ManagerSignup, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    company = Company(name=payload.company_name)
    db.add(company)
    db.flush()  # get company.id
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=UserRole.MANAGER,
        company_id=company.id
    )

    db.add(user)
    db.commit()

    return {"message": "Manager and company created successfully"}

@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "company_id": user.company_id
    }

    access_token, expire = create_access_token(token_data)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,          # True in HTTPS
        samesite="lax",
        max_age=30 * 60        # 30 minutes
    )

    return {
        "message": "Login successful",
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {
        "user_id": user["sub"],
        "role": user["role"]
    }
