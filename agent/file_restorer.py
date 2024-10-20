# agent/file_restorer.py

import json
from typing import List, Optional
from agent.schemas import (
    FileMapType,
    FileData,
    ClassInfo,
    BasicInfo,
    FilesEdit,
    FunctionInfo,
)
from pydantic import FilePath
from agent.structure_filter import StructureFilter
from loguru import logger


class FileRestorer:
    def __init__(self, repo_structure_path: FilePath, indent: int = 2):
        with open(repo_structure_path, "r") as f:
            repo_structure_dict = json.load(f)

        self.repo_structure: FileMapType = {
            file_path: FileData.model_validate(file_data)
            for file_path, file_data in repo_structure_dict.items()
        }
        self.indent = " " * indent
        self.filter = StructureFilter(self.repo_structure)

    def restore_all_files(self, process_first_only: bool = False) -> str:
        """还原所有文件内容。如果 process_first_only 为 True，则只处理第一个文件。"""
        all_file_contents = []

        for index, (file_path, file_data) in enumerate(self.repo_structure.items()):
            if process_first_only and index > 0:
                break

            file_lines = self._restore_single_file(file_data)
            file_lines.sort(key=lambda x: int(x.split(":")[0]))
            file_header = f"# 文件: {file_path}\n"
            all_file_contents.append(file_header + "\n".join(file_lines))

        return "\n\n".join(all_file_contents)

    def restore_files_from_issues(self, issues_json_str: str) -> str:
        """根据问题列表还原指定的文件内容。"""
        files_edit = FilesEdit.model_validate_json(issues_json_str)
        filtered_structure = self.filter.filter_structure_from_issues(files_edit)

        return self._restore_files(filtered_structure)

    def _restore_files(self, file_structure: FileMapType) -> str:
        """根据给定的文件结构还原文件内容。"""
        all_file_contents = []
        for file_path, file_data in file_structure.items():
            file_lines = self._restore_single_file(file_data)
            file_lines.sort(key=lambda x: int(x.split(":")[0]))
            file_header = f"# 文件: {file_path}\n"
            all_file_contents.append(file_header + "\n".join(file_lines))
        return "\n\n".join(all_file_contents)

    def _restore_single_file(self, file_data: FileData) -> List[str]:
        """还原单个文件的内容，返回带有行号的行列表。"""
        lines = []

        # 处理导入
        for imp in file_data.imports:
            lines.extend(self._process_section(imp))

        # 处理顶级表达式
        for top_level in file_data.top_level:
            lines.extend(self._process_section(top_level))

        # 处理类和其方法
        for cls in file_data.classes:
            class_text = self._process_class(cls)
            lines.extend(class_text)

        # 处理顶级函数
        for func in file_data.functions:
            logger.success(f"func: {func}")
            lines.extend(self._process_section(func))

        return lines

    def _process_section(
        self,
        section: BasicInfo | FunctionInfo,
    ) -> List[str]:
        """处理文件的一个部分，添加行号。"""
        numbered_lines = []
        section_start_line = section.start_line
        section_lines = section.text.split("\n")

        if isinstance(section, FunctionInfo) and section.trimmed_code_start_line:
            # 如果存在 trimmed_code_start_line，说明文本包含了 sketch，需要调整行号
            sketch_lines = section.sketch.split("\n") if section.sketch else []
            num_sketch_lines = len(sketch_lines)
            # trimmed_code_start_line 为选定代码的原始起始行号
            code_current_line = section.trimmed_code_start_line
        else:
            num_sketch_lines = 0
            code_current_line = section_start_line

        current_line = section_start_line

        for i, line in enumerate(section_lines):
            if i < num_sketch_lines:
                # 对于 sketch 部分，使用 section_start_line 作为行号
                numbered_lines.append(f"{current_line + i}: {self.indent}{line}")
            else:
                # 对于选定的代码部分，使用 code_current_line
                numbered_lines.append(f"{code_current_line}: {self.indent}{line}")
                code_current_line += 1

        return numbered_lines

    def _process_class(self, cls: ClassInfo) -> List[str]:
        """处理类信息，包括装饰器、表达式和函数。"""
        lines = []

        # 处理类装饰器
        for decorator in cls.class_decorators:
            decorator_line = decorator.start_line
            lines.append(f"{decorator_line}: {self.indent}{decorator.decorator_name}")

        # 添加类定义
        lines.append(f"{cls.start_line}: {self.indent}class {cls.class_name}:")

        # 添加类内的表达式
        for expr in cls.expressions:
            expr_lines = self._process_section(expr)
            expr_lines = [
                f"{line.split(':')[0]}: {self.indent}{line.split(':', 1)[1]}"
                for line in expr_lines
            ]
            lines.extend(expr_lines)

        # 添加类内的函数
        for func in cls.functions:
            func_lines = self._process_section(func)
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
