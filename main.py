from typing import Union
from fastapi import FastAPI
import logging

from app.routes import health
from app.routes import auth

from app.db.database import engine
from app.models import company
from sqlalchemy import text
from app.routes import task
from app.routes import user

from app.core.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

company.Base.metadata.create_all(bind=engine)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(task.router)
app.include_router(user.router)

# Rate Limiting Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logging.info("✅ Database connected successfully (SQLite)")
except Exception as e:
    logging.error(f"❌ Database connection failed: {e}")
