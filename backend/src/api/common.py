from enum import Enum


class Status(Enum):
    TODO: int = "todo"
    DOING: int = "doing"
    BLOCKED: int = "blocked"
    DONE: int = "done"


class Priority(Enum):
    LOW: int = -1
    MEDIUM: int = 0
    HIGH: int = 1


class Type(Enum):
    EPIC: str = "epic"
    FEATURE: str = "feature"
    STORY: str = "story"
    TASK: str = "task"
    BUG: str = "bug"
