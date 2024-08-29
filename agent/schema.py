from pydantic import BaseModel, Field
from typing import List, Dict


class BasicInfo(BaseModel):
    start_line: int
    end_line: int
    text: str


class Expressioninfo(BasicInfo):
    pass


class FunctionInfo(BasicInfo):
    """Model to represent function information."""

    function_name: str
    sketch: str


class ClassInfo(BaseModel):
    """Model to represent class information."""

    class_name: str
    class_decorators: List[str] = Field(default_factory=list)
    expressions: List[Expressioninfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)


class ImportInfo(BasicInfo):
    pass


class FileData(BaseModel):
    """Model to represent file data."""

    imports: List[ImportInfo] = Field(default_factory=list)
    classes: List[ClassInfo] = Field(default_factory=list)
    top_level: List[str] = Field(default_factory=list)


FileMapType = Dict[str, FileData]
