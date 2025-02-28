import pathlib
import sqlite3
import pytest
from todo.core import domain
from todo.repositories import db_task_repo


@pytest.fixture
def database_uri(tmp_path: pathlib.Path):
    return f"{tmp_path}.db"


@pytest.fixture
def gateway(database_uri: str):
    return db_task_repo.DBGateway(database_uri)


@pytest.fixture
def test_cursor(database_uri: str):
    conn = sqlite3.connect(database_uri)
    return conn.cursor()


@pytest.fixture
def repo_builder_without_gateway():
    return db_task_repo.TaskDBRepoBuilder()


@pytest.fixture
def repo_builder(
    repo_builder_without_gateway: db_task_repo.TaskDBRepoBuilder,
    database_uri: str,
) -> db_task_repo.TaskDBRepoBuilder:
    repo_builder_without_gateway.build_gateway(database_uri)
    return repo_builder_without_gateway


class TestRepoBuilder:

    def test_build_fails_without_gateway(
        self, repo_builder_without_gateway: db_task_repo.TaskDBRepoBuilder
    ) -> None:
        with pytest.raises(ValueError, match="gateway has not been set") as err:
            _ = repo_builder_without_gateway.build()

    def test_build_gateway(
        self,
        repo_builder: db_task_repo.TaskDBRepoBuilder,
        test_cursor: sqlite3.Cursor,
    ) -> None:
        test_cursor = test_cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table';"""
        )
        observed = test_cursor.fetchall()

        assert observed == [("Task",)]

    def test_build_repo(self, repo_builder: db_task_repo.TaskDBRepoBuilder):
        observed = repo_builder.build()
        assert isinstance(observed, db_task_repo.TaskDBRepo)


class TestRepo:
    @pytest.fixture
    def repo(
        self, repo_builder: db_task_repo.TaskDBRepoBuilder
    ) -> db_task_repo.TaskDBRepo:
        return repo_builder.build()

    def test_add_task(self, repo: db_task_repo.TaskDBRepo, test_cursor: sqlite3.Cursor):
        given = domain.TaskDraft("test_name")
        repo.add_task(given)

        observed = test_cursor.execute("SELECT * FROM TASK").fetchall()
        assert [(1, "test_name")] == observed


class TestQueryBuilders:
    # TODO: Maybe refactor to not use fixture
    @pytest.fixture
    def test_data(self, request: pytest.FixtureRequest):
        return request.param["assembler"], request.param["expected"]

    @pytest.mark.parametrize(
        "test_data",
        [
            {
                "id": "Task Table Create",
                "assembler": db_task_repo.CreateTaskTableAssembler(),
                # fmt: off
                "expected": 'CREATE TABLE "Task" ' \
                         +  '("id" INTEGER PRIMARY KEY NOT NULL,' \
                         +  '"name" TEXT NOT NULL)',
                # fmt: on
            },
            {
                "id": "Add Task",
                "assembler": db_task_repo.AddTaskAssembler(),
                "expected": 'INSERT INTO "Task" ("name") VALUES (:name)',
            },
        ],
        indirect=True,
        ids=lambda x: x["id"],
    )
    def test_build_query(self, test_data: tuple[db_task_repo.QueryAssembler, str]):
        assembler, expected = test_data
        assert assembler.assemble_query() == expected
