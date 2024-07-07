# test_schemas.py
import pytest
from pydantic import ValidationError, HttpUrl
from pathlib import Path
from agent.schemas import RepoCloneConfig


def test_repo_clone_config_valid_url(tmp_path):
    config = RepoCloneConfig(
        target_repo_url="https://github.com/user/repo.git",
        workspace_path=tmp_path,
    )
    assert config.target_repo_url == HttpUrl("https://github.com/user/repo.git")


def test_repo_clone_config_valid_name(tmp_path):
    config = RepoCloneConfig(
        target_repo_name="user/repo",
        workspace_path=tmp_path,
    )
    assert config.target_repo_name == "user/repo"


def test_repo_clone_config_valid_path(tmp_path):
    config = RepoCloneConfig(
        target_repo_path=tmp_path,
        workspace_path=tmp_path,
    )
    assert config.target_repo_path == tmp_path
    assert config.workspace_path == tmp_path


def test_repo_clone_config_no_option(tmp_path):
    with pytest.raises(ValidationError):
        RepoCloneConfig(
            workspace_path=Path(tmp_path),
        )


def test_repo_clone_config_multiple_options(tmp_path):
    with pytest.raises(ValidationError):
        RepoCloneConfig(
            target_repo_url="https://github.com/user/repo.git",
            target_repo_name="user/repo",
            workspace_path=tmp_path,
        )


def test_serialize_model_with_url(tmp_path):
    config = RepoCloneConfig(
        target_repo_url="https://github.com/user/repo.git",
        workspace_path=tmp_path,
    )
    repo_info = config.model_dump()
    assert repo_info == {
        "url": "https://github.com/user/repo.git",
        "workspace_path": tmp_path,
    }


def test_serialize_model_with_name(tmp_path):
    config = RepoCloneConfig(
        target_repo_name="user/repo",
        workspace_path=tmp_path,
    )
    repo_info = config.model_dump()
    assert repo_info == {
        "url": "https://github.com/user/repo.git",
        "workspace_path": tmp_path,
    }


def test_serialize_model_with_path(tmp_path):
    config = RepoCloneConfig(
        target_repo_path=tmp_path,
        workspace_path=tmp_path,
    )
    repo_info = config.model_dump()
    assert repo_info == {
        "path": tmp_path,
        "workspace_path": tmp_path,
    }
