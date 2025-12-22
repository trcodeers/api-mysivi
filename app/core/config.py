import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)
BCRYPT_ROUNDS = 12

class RateLimits:
    signup = "1/minute"
    login = "3/minute"
    create_reportee = "20/minute"
    task_list = "5/minute"
    task_assign = "2/minute"
    task_delete = "1/minute"
    task_status_update = "3/minute"
    task_status_self_update = "5/minute"
    task_create = "10/minute"

RATE_LIMITS = RateLimits()


TASK_LIST_PAGINATION_SIZE = 5