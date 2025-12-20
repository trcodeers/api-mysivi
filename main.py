from typing import Union
from fastapi import FastAPI

from app.routes import health

from app.db.database import engine
from app.models import company

company.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(health.router)
