from enum import Enum

class UserRole(str, Enum):
    MANAGER = "MANAGER"
    REPORTEE = "REPORTEE"
