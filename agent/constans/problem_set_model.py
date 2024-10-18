from pydantic import BaseModel, field_validator
from typing import List


class Problem(BaseModel):
    description: str
    code: List[str] | str
    planning: str

    @field_validator("code")
    @classmethod
    def join_code_lines(cls, code: List[str]) -> str:
        # Check if the input is a list of strings and then join them into a single string
        if isinstance(code, list):
            return "\\n".join(code)
        return code


class Algorithm(BaseModel):
    tutorial: str

    @field_validator("tutorial")
    @classmethod
    def replace_newlines(cls, tutorial: str) -> str:
        """
        This method replaces all newline characters in the tutorial with \\n.
        """
        return tutorial.replace("\n", "\\n")


class ProblemSet(BaseModel):
    problems: List[Problem]
    algorithm: Algorithm
