# agent/schemas.py
from typing import Annotated, Optional, Self, List, Dict
from pydantic import (
    AnyUrl,
    Field,
    UrlConstraints,
    BaseModel,
    StringConstraints,
    DirectoryPath,
    model_validator,
    model_serializer,
)

GitUrl = Annotated[
    AnyUrl, UrlConstraints(max_length=2083, allowed_schemes=["http", "https", "git"])
]
"""A type that represents the URL of the GitHub repository to clone."""

RepoName = Annotated[
    str, StringConstraints(strip_whitespace=True, to_lower=True, pattern=r".*\/.*")
]
"""A type that represents the name of the repository, which must include '/'."""


class RepoCloneConfig(BaseModel):
    target_repo_url: Optional[GitUrl] = None
    target_repo_name: Optional[RepoName] = None
    target_repo_path: Optional[DirectoryPath] = None
    workspace_path: DirectoryPath

    @model_validator(mode="after")
    def check_one_of(self) -> Self:
        target_repo_url = self.target_repo_url
        target_repo_name = self.target_repo_name
        target_repo_path = self.target_repo_path

        if not any([target_repo_url, target_repo_name, target_repo_path]):
            raise ValueError(
                "One of 'target_repo_url', 'target_repo_name', or 'target_repo_path' must be provided."
            )

        if sum(map(bool, [target_repo_url, target_repo_name, target_repo_path])) > 1:
            raise ValueError(
                "Only one of 'target_repo_url', 'target_repo_name', or 'target_repo_path' can be provided."
            )

        return self

    @model_serializer()
    def serialize_model(self):
        if self.target_repo_path is not None:
            repo_info = {
                "path": self.target_repo_path,
                "workspace_path": self.workspace_path,
            }
        else:
            if self.target_repo_url is not None:
                repo_url = str(self.target_repo_url)
            elif self.target_repo_name is not None:
                repo_url = f"https://github.com/{self.target_repo_name}.git"

            repo_info = {"url": repo_url, "workspace_path": self.workspace_path}

        return repo_info


class BasicInfo(BaseModel):
    start_line: int
    end_line: int
    text: str


class ExpressionInfo(BasicInfo):
    pass


class TopLevelInfo(BasicInfo):
    pass


class FunctionInfo(BasicInfo):
    """Model to represent function information."""

    function_name: str
    sketch: str


class ClassInfo(BaseModel):
    """Model to represent class information."""

    class_name: str
    class_decorators: List[str] = Field(default_factory=list)
    expressions: List[ExpressionInfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)


class ImportInfo(BasicInfo):
    pass


class FileData(BaseModel):
    """Model to represent file data."""

    imports: List[ImportInfo] = Field(default_factory=list)
    classes: List[ClassInfo] = Field(default_factory=list)
    top_level: List[TopLevelInfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)


FileMapType = Dict[str, FileData]
