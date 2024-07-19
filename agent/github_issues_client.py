import httpx
from typing import Dict, Any, List


class GitHubIssuesClient:
    """
    An asynchronous client for interacting with the GitHub API for issues.

    The client can be initialized without a GitHub token, but the token can be set in the environment variables.

    Examples:
        >>> client = GitHubIssuesClient()
        >>> issue = await client.get_issue("owner", "repo", issue_number)
        >>> comments = await client.get_issue_comments("owner", "repo", issue_number)
    """

    DEFAULT_BASE_URL = "https://api.github.com"
    DEFAULT_API_VERSION = "2022-11-28"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_version: str = DEFAULT_API_VERSION,
    ) -> None:
        """
        Initialize the GitHubIssuesClient.

        Args:
            - base_url (str): Base URL for the GitHub API (defaults to "https://api.github.com").
            - api_version (str): GitHub API version (defaults to "2022-11-28").
        """
        self._base_url = base_url
        self._api_version = api_version

        self._endpoints = {
            "getIssue": "/repos/{owner}/{repo}/issues/{issue_number}",
            "getIssueComments": "/repos/{owner}/{repo}/issues/{issue_number}/comments",
        }

        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": f"{self._api_version}",
        }

    def get_all_endpoints(self) -> Dict[str, str]:
        """Get all available endpoints."""
        return {**self._endpoints}

    async def request(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, Any] = {},
        params: Dict[str, Any] = {},
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Makes an API request to the GitHub API.

        Args:
            - endpoint (str): Name of the endpoint to make the request to.
            - method (str): HTTP method to use for the request.
            - headers (dict): HTTP headers to include in the request.
            - params (dict): Query parameters to include in the request.
            - kwargs: Keyword arguments to pass to the endpoint URL.

        Returns:
            - response (httpx.Response): Response from the API request.

        Raises:
            - httpx.HTTPStatusError: If the API request fails.
        """
        _headers = {**self._headers, **headers}

        async with httpx.AsyncClient(
            headers=_headers, base_url=self._base_url, params=params
        ) as _client:
            try:
                response = await _client.request(
                    method, url=self._endpoints[endpoint].format(**kwargs)
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as excp:
                if excp.response.status_code == 404:
                    print(f"Resource not found for {excp.request.url}")
                elif excp.response.status_code == 410:
                    print(f"Resource gone for {excp.request.url}")
                elif excp.response.status_code == 301:
                    print(f"Resource moved permanently for {excp.request.url}")
                elif excp.response.status_code == 304:
                    print(f"Resource not modified for {excp.request.url}")
                else:
                    print(f"HTTP Exception for {excp.request.url} - {excp}")
                raise excp
            return response

    async def get_issue_description(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> Dict[str, str]:
        """
        Get a single issue description from a repository.

        Args:
            - owner (str): Owner of the repository.
            - repo (str): Name of the repository.
            - issue_number (int): Number of the issue.

        Returns:
            - A dictionary with the issue details including title and body.

        Examples:
            >>> issue = await client.get_issue("owner", "repo", 1)
        """
        response = await self.request(
            endpoint="getIssue",
            method="GET",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
        )
        data = response.json()
        return {
            "title": data.get("title"),
            "body": data.get("body"),
            "author": data.get("user", {}).get("login"),
        }

    async def get_issue_comments(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> List[Dict[str, str]]:
        """
        Get comments of a single issue from a repository.

        Args:
            - owner (str): Owner of the repository.
            - repo (str): Name of the repository.
            - issue_number (int): Number of the issue.

        Returns:
            - A list of dictionaries, each containing the comment details including user and body.

        Examples:
            >>> comments = await client.get_issue_comments("owner", "repo", 1)
        """
        response = await self.request(
            endpoint="getIssueComments",
            method="GET",
            owner=owner,
            repo=repo,
            issue_number=issue_number,
        )
        comments_data = response.json()
        comments = []
        for comment in comments_data:
            comments.append(
                {
                    "user": comment.get("user", {}).get("login"),
                    "body": comment.get("body"),
                }
            )
        return comments

    async def get_issue_and_comments_markdown(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> str:
        """
        Get a single issue and its comments from a repository, and return them as a markdown string.

        Args:
            - owner (str): Owner of the repository.
            - repo (str): Name of the repository.
            - issue_number (int): Number of the issue.

        Returns:
            - A markdown formatted string containing the issue details and comments.

        Examples:
            >>> markdown = await client.get_issue_and_comments_markdown("owner", "repo", 1)
        """
        # Get issue details
        issue = await self.get_issue(owner, repo, issue_number)

        # Get issue comments
        comments = await self.get_issue_comments(owner, repo, issue_number)

        # Create markdown string
        markdown = f"# {issue['title']}\n\n"
        markdown += f"**Author**: {issue['author']}\n\n"
        markdown += f"{issue['body']}\n\n"
        markdown += "---\n\n"
        markdown += "## Comments\n\n"

        for comment in comments:
            markdown += f"**{comment['user']}**:\n\n"
            markdown += f"{comment['body']}\n\n"
            markdown += "---\n\n"

        return markdown


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Test the GitHubIssuesClient."""
        client = GitHubIssuesClient()

        markdown = await client.get_issue_and_comments_markdown(
            owner="OpenBMB", repo="RepoAgent", issue_number=59
        )

        print(markdown)

    asyncio.run(main())
