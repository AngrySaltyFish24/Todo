from collections.abc import Mapping
from enum import Enum
from typing import Any

import flask
import jsonschema

from todo.core import domain, interactor

from todo import repositories


# TODO: Use dictionary instead of enum
class Schema(Enum):
    ADD_TASK = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "additionalProperties": False,
        "required": ["name"],
    }


class NoJsonError(Exception):
    pass


# TODO: Make recursive type to avoid Any
def get_validated_payload(schema: Schema) -> Mapping[str, Any]:
    if not flask.request.is_json:
        raise NoJsonError

    payload: Mapping[str, Any] = flask.request.get_json()
    jsonschema.validate(payload, schema.value)
    return payload


def create_app(_interactor: interactor.Interactor) -> flask.Flask:
    app = flask.Flask(__name__)

    @app.route("/v1/add_task", methods=["POST"])
    def add_task() -> tuple[str, int]:
        try:
            payload: Mapping[str, str] = get_validated_payload(Schema.ADD_TASK)
        except NoJsonError:
            return "Please set headers to JSON/Application", 400
        except jsonschema.ValidationError as err:
            return err.message, 400

        task_draft = domain.TaskDraft(payload["name"])
        _interactor.add_task(task_draft)
        return "Hello World", 200

    @app.route("/v1/hello")
    def hello() -> str:
        return "Hello World"

    return app


def main() -> None:
    repo_builder = repositories.TaskDBRepoBuilder()
    repo_builder.build_gateway("database.db")
    _interactor = interactor.Interactor(repo_builder.build())
    app = create_app(_interactor)
    app.run()


if __name__ == "__main__":
    main()
