from typing import Final
import abc

from todo.core import domain


class TaskRepo(abc.ABC):
    @abc.abstractmethod
    def add_task(self, task_draft: domain.TaskDraft) -> None:
        raise NotImplementedError


class Interactor:
    def __init__(self, task_repo: TaskRepo) -> None:
        self.task_repo: Final[TaskRepo] = task_repo

    def add_task(self, task_draft: domain.TaskDraft) -> None:
        self.task_repo.add_task(task_draft)
