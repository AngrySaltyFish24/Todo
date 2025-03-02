import mock

from todo import core
from todo.core import domain


def make_test_interator(mock_task_repo: None | core.TaskRepo = None):
    if mock_task_repo is None:
        mock_task_repo = mock.Mock(spec_set=core.TaskRepo)

    return core.Interactor(mock_task_repo)


def test_interactor():
    _mock = mock.Mock(spec_set=core.TaskRepo)

    _interactor = make_test_interator(_mock)
    task_draft = domain.TaskDraft("Test")
    _ = _interactor.add_task(task_draft)

    _mock.add_task.assert_called_once_with(task_draft)
