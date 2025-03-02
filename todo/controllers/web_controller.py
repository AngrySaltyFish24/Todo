import dataclasses
import enum
from collections.abc import Mapping
from typing import Any

import flask
import jsonschema

from todo import repositories
from todo.core import domain, interactor


# TODO: Use dictionary instead of enum
class Schema(enum.Enum):
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
    def add_task() -> tuple[str, int] | flask.Response:
        try:
            payload: Mapping[str, str] = get_validated_payload(Schema.ADD_TASK)
        except NoJsonError:
            return "Please set headers to JSON/Application", 400
        except jsonschema.ValidationError as err:
            return err.message, 400

        task_draft = domain.TaskDraft(payload["name"])
        created_task = _interactor.add_task(task_draft)
        created_task = dataclasses.asdict(created_task)

        return flask.jsonify(created_task)

    return app


def main() -> None:
    repo_builder = repositories.TaskDBRepoBuilder()
    repo_builder.build_gateway("database.db")
    _interactor = interactor.Interactor(repo_builder.build())
    app = create_app(_interactor)
    app.run()


if __name__ == "__main__":
    main()
