from enum import Enum


class Status(Enum):
    TODO: str = "todo"
    DOING: str = "doing"
    BLOCKED: str = "blocked"
    DONE: str = "done"


class Priority(Enum):
    LOW: int = -1
    MEDIUM: int = 0
    HIGH: int = 1
