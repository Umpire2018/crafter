import click
from agent.console import console, set_theme
from pathlib import Path
from agent.repo import clone_repo


@click.group()
@click.option(
    "--theme",
    type=click.Choice(["light", "dark"]),
    default="light",
    help="Choose theme: light or dark",
)
def main(theme):
    set_theme(theme)


@main.command()
@click.option(
    "--target-repo-url",
    "target_repo_url",
    required=False,
    type=str,
    help="The URL of the repository to clone. Example: 'https://github.com/octocat/Hello-World.git'.",
)
@click.option(
    "--target-repo-name",
    "target_repo_name",
    required=False,
    type=str,
    help="The name of the repository to clone. Example: 'octocat/Hello-World'.",
)
@click.option(
    "--target-repo-path",
    "target_repo_path",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="The local path of the repository. Example: '/path/to/local/repo'.",
)
@click.option(
    "--target-repo-commit-hash",
    "target_repo_commit_hash",
    required=False,
    type=str,
    help="The commit hash of the repository to clone. Example: 'a1b2c3d4e5f6'.",
)
@click.option(
    "--workspace-path",
    "workspace_path",
    required=False,
    default="./workspace",
    type=click.Path(file_okay=False, path_type=Path),
    help="The path to the workspace where the repository will be cloned. Example: '/path/to/workspace'.",
)
def run(
    target_repo_url,
    target_repo_name,
    target_repo_path,
    workspace_path,
    target_repo_commit_hash,
):
    """
    Clones a repository to the specified workspace path.

    Note: One of URL, NAME, or PATH must be provided.
    """
    console.print("Run command executed", style="info")

    # Ensure workspace_path exists and create it if it doesn't
    if not workspace_path.exists():
        workspace_path.mkdir(parents=True)
        console.print(f"Created workspace directory: {workspace_path}", style="info")

    clone_repo(
        target_repo_url=target_repo_url,
        target_repo_name=target_repo_name,
        target_repo_path=target_repo_path,
        workspace_path=workspace_path,
        target_repo_commit_hash=target_repo_commit_hash,
    )


if __name__ == "__main__":
    main()
