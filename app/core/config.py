from datetime import timedelta

JWT_SECRET_KEY = "CHANGE_ME_SUPER_SECRET"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


class RateLimits:
    signup = "5/minute"
    login = "5/minute"
    create_reportee = "20/minute"
    task_list = "5/minute"
    task_assign = "2/minute"
    task_delete = "1/minute"
    task_status_update = "3/minute"
    task_status_self_update = "5/minute"
    task_create = "3/minute"

RATE_LIMITS = RateLimits()
