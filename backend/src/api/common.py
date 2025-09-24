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


class Type(Enum):
    EPIC: str = "epic"
    FEATURE: str = "feature"
    SPIKE: str = "spike"
    STORY: str = "story"
    TASK: str = "task"
    BUG: str = "bug"
