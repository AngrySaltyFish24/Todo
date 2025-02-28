from todo.core import interactor, domain
import pytest
import mock


def make_test_interator(mock_task_repo: None | interactor.TaskRepo = None):
    if mock_task_repo is None:
        mock_task_repo = mock.Mock(spec_set=interactor.TaskRepo)

    return interactor.Interactor(mock_task_repo)


def test_interactor():
    _mock = mock.Mock(spec_set=interactor.TaskRepo)

    _interactor = make_test_interator(_mock)
    task_draft = domain.TaskDraft("Test")
    _interactor.add_task(task_draft)

    _mock.add_task.assert_called_once_with(task_draft)
