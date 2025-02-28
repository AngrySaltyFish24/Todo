import sqlite3
import abc
from typing import Final, Mapping, override, Any

from todo.core import domain, interactor


import pypika


class TablesMixin:
    TASK: Final[pypika.Table] = pypika.Table("Task")


class QueryAssembler(abc.ABC):
    def assemble_query(self) -> str:
        raise NotImplementedError


class CreateTaskTableAssembler(QueryAssembler, TablesMixin):
    @override
    def assemble_query(self) -> str:
        query = pypika.Query.create_table(self.TASK).columns(
            pypika.Column("id", "INTEGER PRIMARY KEY", nullable=False),
            pypika.Column("name", "TEXT", nullable=False),
        )

        return str(query)


class AddTaskAssembler(QueryAssembler, TablesMixin):

    def _format_name_param(self, field_name: str) -> str:
        return f":{field_name}"

    @override
    def assemble_query(self) -> str:
        query = (
            pypika.Query.into(self.TASK)
            .columns("name")
            .insert(pypika.Parameter(self._format_name_param("name")))
        )

        return str(query)


class DBGateway:
    def __init__(self, connection_uri: str) -> None:
        # At current use a single connection for single thread access, more
        # connections could by added and store in a queue for a proper pool
        self.uri: Final[str] = connection_uri

    def _create_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.uri)

    # TODO: Seperate into read and write
    def _execute_query(
        self, query: str, params: Mapping[str, str | int] | None = None
    ) -> list[Any]:
        if params is None:
            params = {}

        conn = self._create_connection()
        cursor = conn.cursor()
        cursor = cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()

    def create_tables(self) -> None:
        table_assemblers = [CreateTaskTableAssembler()]

        for assembler in table_assemblers:
            _ = self._execute_query(assembler.assemble_query())

    def add_task(self, task_draft: domain.TaskDraft) -> None:
        query = AddTaskAssembler().assemble_query()
        params = {"name": task_draft.name}
        _ = self._execute_query(query, params)


class TaskDBRepo(interactor.TaskRepo):
    def __init__(self, gateway: DBGateway) -> None:
        self.gateway: Final[DBGateway] = gateway

    @override
    def add_task(self, task_draft: domain.TaskDraft) -> None:
        self.gateway.add_task(task_draft)


class TaskDBRepoBuilder:
    def __init__(self) -> None:
        self.gateway: DBGateway | None = None

    def build_gateway(self, connection_uri: str) -> None:
        self.gateway = DBGateway(connection_uri)
        self.gateway.create_tables()

    def build(self) -> TaskDBRepo:
        if self.gateway is None:
            raise ValueError("gateway has not been set, ensure build_gateway is called")

        return TaskDBRepo(self.gateway)
