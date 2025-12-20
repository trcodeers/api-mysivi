from pydantic import BaseModel

class ManagerSignup(BaseModel):
    company_name: str
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str
