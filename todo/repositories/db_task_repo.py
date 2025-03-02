import abc
import sqlite3
from collections.abc import Mapping
from typing import Final, override

import pypika
import pypika.enums
import pypika.functions

from todo import core
from todo.core import domain


class TablesMixin:
    TASK: Final[pypika.Table] = pypika.Table("Task")


class ParamMixin:
    def _format_name_param(self, field_name: str) -> str:
        return f":{field_name}"


class QueryAssembler(abc.ABC):
    def assemble_query(self) -> str:
        raise NotImplementedError


class CreateTaskTableAssembler(QueryAssembler, TablesMixin):
    @override
    def assemble_query(self) -> str:
        query = (
            pypika.Query.create_table(self.TASK)
            .columns(
                pypika.Column("id", "INTEGER PRIMARY KEY", nullable=False),
                pypika.Column("name", "TEXT", nullable=False),
                pypika.Column(
                    "date_added",
                    pypika.enums.SqlTypes.TIMESTAMP,
                    default=pypika.functions.CurTimestamp(),
                ),
            )
            .if_not_exists()
        )

        return str(query)


class AddTaskAssembler(QueryAssembler, TablesMixin, ParamMixin):
    @override
    def assemble_query(self) -> str:
        query = (
            pypika.Query.into(self.TASK)
            .columns("name")
            .insert(pypika.NamedParameter("name"))
        )

        return str(query) + " RETURNING *"


class DBGateway:
    def __init__(self, connection_uri: str) -> None:
        # At current use a single connection for single thread access, more
        # connections could by added and store in a queue for a proper pool
        self.uri: Final[str] = connection_uri

    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.uri)
        conn.row_factory = sqlite3.Row
        return conn

    # TODO: Seperate into read and write
    def _execute_query(
        self, query: str, params: Mapping[str, str | int] | None = None
    ) -> list[sqlite3.Row]:
        if params is None:
            params = {}

        # TODO: Add error handling and rollback
        conn = self._create_connection()
        cursor = conn.cursor()
        cursor = cursor.execute(query, params)
        results = cursor.fetchall()
        conn.commit()
        return results

    def create_tables(self) -> None:
        table_assemblers = [CreateTaskTableAssembler()]

        for assembler in table_assemblers:
            _ = self._execute_query(assembler.assemble_query())

    def add_task(self, task_draft: domain.TaskDraft) -> sqlite3.Row:
        query = AddTaskAssembler().assemble_query()
        params = {"name": task_draft.name}
        results = self._execute_query(query, params)
        return results[0]


class TaskDBRepo(core.TaskRepo):
    def __init__(self, gateway: DBGateway) -> None:
        self.gateway: Final[DBGateway] = gateway

    @override
    def add_task(self, task_draft: domain.TaskDraft) -> domain.Task:
        inserted_row = self.gateway.add_task(task_draft)
        return domain.make_task_from_draft(task_draft, inserted_row["date_added"])


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
