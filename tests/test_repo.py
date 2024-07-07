# test_repo.py
import pytest
from agent.repo import clone_repo
from agent.console import console

@pytest.fixture
def mock_console_print(monkeypatch):
    def mock_print(*args, **kwargs):
        pass
    
    monkeypatch.setattr(console, 'print', mock_print)

def test_clone_repo_with_path(monkeypatch, mock_console_print, tmp_path):
    clone_repo(
        workspace_path=tmp_path,
        target_repo_path=tmp_path,
    )
    
    # Verify that Repo.clone_from is not called
    def mock_clone_from(*args, **kwargs):
        raise AssertionError("Repo.clone_from should not be called when target_repo_path is provided.")
    
    monkeypatch.setattr("agent.repo.Repo.clone_from", mock_clone_from)


def test_clone_repo_with_url(monkeypatch, mock_console_print, tmp_path):
    cloned_url = None
    cloned_path = None

    def mock_clone_from(url, path):
        nonlocal cloned_url, cloned_path
        cloned_url = url
        cloned_path = path

    monkeypatch.setattr("agent.repo.Repo.clone_from", mock_clone_from)

    clone_repo(
        workspace_path=tmp_path,
        target_repo_url="https://github.com/user/repo.git",
    )
    
    assert cloned_url == "https://github.com/user/repo.git"
    assert cloned_path == tmp_path


def test_clone_repo_with_invalid_config(monkeypatch, tmp_path):
    error_message = None

    def mock_print(message, style=None):
        nonlocal error_message
        if style == "error":
            error_message = message

    monkeypatch.setattr(console, 'print', mock_print)

    with pytest.raises(Exception):
        clone_repo(
            workspace_path=tmp_path,
        )

    assert "Validation error" in error_message
