from datetime import timedelta

JWT_SECRET_KEY = "CHANGE_ME_SUPER_SECRET"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


class RateLimits:
    signup = "5/hour"
    login = "10/minute"
    create_reportee = "20/hour"
    task_list = "50/hour"
    task_assign = "20/hour"
    task_delete = "10/hour"
    task_status_update = "30/hour"
    task_status_self_update = "50/hour"
    task_create = "30/hour"

RATE_LIMITS = RateLimits()
