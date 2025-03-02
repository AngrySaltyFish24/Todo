import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Task:
    name: str
    date_added: datetime


@dataclasses.dataclass
class TaskDraft:
    name: str


def make_task(draft: TaskDraft, date_added: datetime) -> Task:
    return Task(draft.name, date_added)
