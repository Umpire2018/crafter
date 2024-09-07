# agent/file_restorer.py
import json
from typing import List
from agent.schemas import (
    FileMapType,
    FileData,
    ClassInfo,
    BasicInfo,
)
from pydantic import FilePath


class FileRestorer:
    def __init__(self, repo_structure_path: FilePath, indent: int = 2):
        with open(repo_structure_path, "r") as f:
            repo_structure_dict = json.load(f)

        # Manually parse each value in the dictionary as a Pydantic model
        self.repo_structure: FileMapType = {
            file_path: FileData.model_validate(file_data)
            for file_path, file_data in repo_structure_dict.items()
        }
        self.indent = " " * indent  # Set indentation, default is 2 spaces

    def restore_all_files(self, process_first_only: bool = True) -> str:
        """Restore file contents. If process_first_only is True, only process the first file."""
        all_lines = []
        file_headers = []

        # Use enumerate to iterate over the file paths and their respective data
        for index, (file_path, file_data) in enumerate(self.repo_structure.items()):
            if process_first_only and index > 0:
                break  # Only process the first file, exit the loop

            # Add file header with indentation
            file_headers.append(f"# 文件: {file_path}\n")  # Add file identifier
            # Process the current file
            file_lines = self._restore_single_file(file_data)
            all_lines.extend(file_lines)

        # Sort lines by line number, ignoring file headers
        all_lines.sort(key=lambda x: int(x.split(":")[0]))  # Sort lines by line number
        return "\n".join(file_headers + all_lines)

    def _restore_single_file(self, file_data: FileData) -> List[str]:
        """Restore the content of a single file and return a list of lines with line numbers."""
        lines = []

        # Process imports
        for imp in file_data.imports:
            lines.extend(self._process_section(imp))

        # Process top-level expressions
        for top_level in file_data.top_level:
            lines.extend(self._process_section(top_level))

        # Process classes and their methods
        for cls in file_data.classes:
            class_text = self._process_class(cls)
            lines.extend(class_text)

        # Process functions outside of classes
        for func in file_data.functions:
            lines.extend(self._process_section(func))

        return lines

    def _process_section(self, section: BasicInfo) -> List[str]:
        """Process a section of the file, adding line numbers based on start_line."""
        numbered_lines = []
        current_line = section.start_line  # Start from the section's start_line

        # Add line numbers and apply indentation after the line number
        for i, line in enumerate(section.text.split("\n")):
            numbered_lines.append(
                f"{current_line + i}: {self.indent}{line}"
            )  # Add indent after line number
        return numbered_lines

    def _process_class(self, cls: ClassInfo) -> List[str]:
        """Process class information, including decorators, expressions, and functions."""
        lines = []

        # Process class decorators with their line numbers
        for decorator in cls.class_decorators:
            decorator_line = decorator.start_line
            lines.append(f"{decorator_line}: {self.indent}{decorator.decorator_name}")

        # Add class name with its line number
        lines.append(f"{cls.start_line}: {self.indent}class {cls.class_name}:")

        # Add expressions within the class
        for expr in cls.expressions:
            expr_lines = self._process_section(expr)
            # Apply indentation to expressions, ensuring the line number has no indent
            expr_lines = [
                f"{line.split(':')[0]}: {self.indent}{line.split(':', 1)[1]}"
                for line in expr_lines
            ]
            lines.extend(expr_lines)

        # Add functions within the class
        for func in cls.functions:
            func_lines = self._process_section(func)
            # Apply indentation to functions, ensuring the line number has no indent
            func_lines = [
                f"{line.split(':')[0]}: {self.indent}{line.split(':', 1)[1]}"
                for line in func_lines
            ]
            lines.extend(func_lines)

        return lines


if __name__ == "__main__":
    restorer = FileRestorer("filtered_repo_structure.json")
    restored_content = restorer.restore_all_files()

    print(restored_content)
