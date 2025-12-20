from typing import Union
from fastapi import FastAPI
import logging

from app.routes import health

from app.db.database import engine
from app.models import company
from sqlalchemy import text

company.Base.metadata.create_all(bind=engine)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(health.router)



try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logging.info("✅ Database connected successfully (SQLite)")
except Exception as e:
    logging.error(f"❌ Database connection failed: {e}")
