# agent/repo.py
from git import Repo
from agent.console import console
from pydantic import ValidationError
from agent.schemas import GitUrl, RepoName, DirectoryPath, RepoCloneConfig
from pathlib import Path
from typing import Optional


def clone_repo(
    workspace_path: DirectoryPath,
    target_repo_url: Optional[GitUrl] = None,
    target_repo_name: Optional[RepoName] = None,
    target_repo_path: Optional[DirectoryPath] = None,
    target_repo_commit_hash: Optional[str] = None,
):
    try:
        config = RepoCloneConfig(
            target_repo_name=target_repo_name,
            target_repo_path=target_repo_path,
            target_repo_url=target_repo_url,
            workspace_path=workspace_path,
        )
    except ValidationError as e:
        console.print(f"Validation error: {e}", style="error")
        raise

    repo_info = config.model_dump()

    try:
        if "path" in repo_info:
            # If target_repo_path is provided, we don't need to clone
            console.print(
                f"Using local repository '{repo_info['path']}' .", style="info"
            )
            target_repo = Repo(repo_info["path"])

        else:
            repo_url = repo_info["url"]
            console.print(
                f"Cloning repository {repo_url} to {repo_info['workspace_path']}...",
                style="info",
            )
            target_repo = Repo.clone_from(repo_url, repo_info["workspace_path"])
            console.print("Repository cloned successfully.", style="info")

        if target_repo_commit_hash:
            console.print(
                f"Checking out commit hash '{target_repo_commit_hash}'...", style="info"
            )
            target_repo.git.checkout(target_repo_commit_hash)
            return target_repo

    except Exception as e:
        console.print(f"An error occurred: {e}", style="error")
        raise


if __name__ == "__main__":
    clone_repo(
        target_repo_path=Path("."),
        workspace_path=Path("/home/test/arno/Agentless/workspace"),
    )
