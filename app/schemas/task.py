from pydantic import BaseModel, field_validator

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to_id: int | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Task title must be at least 3 characters")
        return v



class TaskAssign(BaseModel):
    assigned_to_id: int
