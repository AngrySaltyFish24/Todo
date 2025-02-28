import abc
from typing import Final

from todo.core import domain


class TaskRepo(abc.ABC):
    @abc.abstractmethod
    def add_task(self, task_draft: domain.TaskDraft) -> domain.Task:
        raise NotImplementedError


class Interactor:
    def __init__(self, task_repo: TaskRepo) -> None:
        self.task_repo: Final[TaskRepo] = task_repo

    def add_task(self, task_draft: domain.TaskDraft) -> domain.Task:
        return self.task_repo.add_task(task_draft)
