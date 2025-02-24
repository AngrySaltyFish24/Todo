from collections.abc import Generator

import flask
import flask.testing
import pytest

from todo.controllers import web_controller


@pytest.fixture()
def app() -> Generator[flask.Flask, None, None]:
    app = web_controller.create_app()
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

    def test_add_task(self, client: flask.testing.FlaskClient):
        resp = client.post("/v1/add_task", json={"name": "test"})
        assert resp.status_code == 200


def test_dummy(client: flask.testing.FlaskClient):
    resp = client.get("/v1/hello")
    assert b"Hello World" in resp.data
