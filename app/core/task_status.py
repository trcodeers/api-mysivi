from enum import Enum

class TaskStatus(str, Enum):
    DEV = "DEV"
    TEST = "TEST"
    STUCK = "STUCK"
    COMPLETED = "COMPLETED"
