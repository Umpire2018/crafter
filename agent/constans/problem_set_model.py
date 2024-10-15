from pydantic import BaseModel
from typing import List

class Problem(BaseModel):
    description: str
    code: List[str]
    planning: str

class Algorithm(BaseModel):
    tutorial: str

class ProblemSet(BaseModel):
    problems: List[Problem]
    algorithm: Algorithm

