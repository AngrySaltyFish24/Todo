import dataclasses
import enum
from collections.abc import Mapping
from typing import Any

import flask
import jsonschema

from todo import core, repositories
from todo.core import domain


# TODO: Change to dictionary with endpoints as keys
class Schema(enum.Enum):
    ADD_TASK = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "additionalProperties": False,
        "required": ["name"],
    }


class NoJsonError(Exception):
    pass


# TODO: Run this on every post with `before_request` and schema dictionary
def get_validated_payload(schema: Schema) -> Mapping[str, Any]:
    if not flask.request.is_json:
        raise NoJsonError

    payload: Mapping[str, Any] = flask.request.get_json()
    jsonschema.validate(payload, schema.value)
    return payload


def create_app(_interactor: core.Interactor) -> flask.Flask:
    app = flask.Flask(__name__)

    @app.route("/v1/add_task", methods=["POST"])
    def add_task() -> tuple[str, int] | flask.Response:
        try:
            payload: Mapping[str, str] = get_validated_payload(Schema.ADD_TASK)
        except NoJsonError:
            return "Please set headers to JSON/Application", 400
        except jsonschema.ValidationError as err:
            return err.message, 400

        task_draft = domain.TaskDraft(payload["name"])
        created_task = _interactor.add_task(task_draft)
        created_task_dict = dataclasses.asdict(created_task)

        return flask.jsonify(created_task_dict)

    return app


def main() -> None:
    repo_builder = repositories.TaskDBRepoBuilder()
    repo_builder.build_gateway("database.db")
    _interactor = core.Interactor(repo_builder.build())
    app = create_app(_interactor)
    app.run()


if __name__ == "__main__":
    main()
