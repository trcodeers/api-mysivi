from fastapi import Depends, HTTPException
from app.core.auth import get_current_user
from app.core.auth import get_current_user

def require_manager(user=Depends(get_current_user)):
    if user["role"] != "MANAGER":
        raise HTTPException(status_code=403, detail="Manager access required")
    return user




def require_reportee(user=Depends(get_current_user)):
    if user["role"] != "REPORTEE":
        raise HTTPException(status_code=403, detail="Reportee access required")
    return user
