from collections.abc import Generator

import flask
import flask.testing
import pytest
import mock

from todo.controllers import web_controller
from todo.core import domain, interactor


@pytest.fixture
def mock_interactor():
    return mock.Mock(spec_set=interactor.Interactor)


@pytest.fixture()
def app(mock_interactor: interactor.Interactor) -> Generator[flask.Flask, None, None]:
    app = web_controller.create_app(mock_interactor)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app: flask.Flask) -> flask.testing.FlaskClient:
    return app.test_client()


class TestAddTask:

    def test_add_task_no_json(self, client: flask.testing.FlaskClient):
        resp = client.post("/v1/add_task", data={"name": "test"})
        assert resp.status_code == 400
        assert b"Please set headers to JSON/Application" in resp.data

    def test_add_task_invalid_json_addtional_property(
        self, client: flask.testing.FlaskClient
    ):
        resp = client.post("/v1/add_task", json={"invalid_name": "test"})
        assert resp.status_code == 400
        assert b"Additional properties are not allowed" in resp.data

    def test_add_task_invalid_json_no_data(self, client: flask.testing.FlaskClient):
        resp = client.post("/v1/add_task", json={})
        assert resp.status_code == 400
        assert b"'name' is a required property" in resp.data

    def test_add_task(
        self, client: flask.testing.FlaskClient, mock_interactor: mock.Mock
    ):
        resp = client.post("/v1/add_task", json={"name": "test"})
        assert resp.status_code == 200

        mock_interactor.add_task.assert_called_once_with(domain.TaskDraft("test"))


def test_dummy(client: flask.testing.FlaskClient):
    resp = client.get("/v1/hello")
    assert b"Hello World" in resp.data
