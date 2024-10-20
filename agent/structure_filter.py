# agent/structure_filter.py

from typing import List
from agent.schemas import (
    FileMapType,
    FileData,
    ClassInfo,
    FunctionInfo,
    FilesEdit,
)
from loguru import logger


class StructureFilter:
    def __init__(self, repo_structure: FileMapType):
        self.repo_structure = repo_structure

    def filter_files(self, file_names: List[str]) -> FileMapType:
        """
        根据文件名列表筛选文件。
        """
        filtered_files = {
            file_name: self.repo_structure[file_name]
            for file_name in file_names
            if file_name in self.repo_structure
        }
        missing_files = set(file_names) - set(filtered_files.keys())
        if missing_files:
            logger.debug(f"以下文件未在仓库结构中找到：{missing_files}")
        return filtered_files

    def filter_classes(self, file_data: FileData, class_names: List[str]) -> FileData:
        """
        根据类名列表筛选类。
        """
        filtered_classes = [
            cls for cls in file_data.classes if cls.class_name in class_names
        ]
        return FileData(
            imports=file_data.imports,
            top_level=file_data.top_level,
            classes=filtered_classes,
            functions=file_data.functions,
        )

    def filter_functions(
        self, class_info: ClassInfo, function_names: List[str]
    ) -> ClassInfo:
        """
        根据函数名列表筛选类中的函数。
        """
        filtered_functions = [
            func
            for func in class_info.functions
            if func.function_name in function_names
        ]
        return ClassInfo(
            class_name=class_info.class_name,
            start_line=class_info.start_line,
            end_line=class_info.end_line,
            class_decorators=class_info.class_decorators,
            expressions=class_info.expressions,
            functions=filtered_functions,
        )

    def filter_structure_from_issues(self, files_edit: FilesEdit) -> FileMapType:
        """
        根据问题列表（issues）中的编辑信息，筛选仓库结构。
        """
        filtered_structure: FileMapType = {}

        for file_edits in files_edit.files:
            file_data = self.repo_structure.get(file_edits.file_name)
            if not file_data:
                logger.debug(f"文件 {file_edits.file_name} 未在仓库结构中找到。")
                continue

            # 创建新的 FileData 实例，复制导入和顶级代码
            new_file_data = FileData(
                imports=file_data.imports,
                top_level=[],
                classes=[],
                functions=[],  # 顶级函数
            )

            for edit in file_edits.edits:
                start_line = edit.line_numbers.start_line
                end_line = edit.line_numbers.end_line

                matched = False

                # 检查类
                for cls in file_data.classes:
                    if cls.start_line <= start_line <= cls.end_line:
                        # 检查是否已在 new_file_data.classes 中存在该类
                        new_class = next(
                            (
                                c
                                for c in new_file_data.classes
                                if c.class_name == cls.class_name
                            ),
                            None,
                        )
                        if not new_class:
                            # 创建新的 ClassInfo 实例并添加到 new_file_data.classes
                            new_class = ClassInfo(
                                class_name=cls.class_name,
                                start_line=cls.start_line,
                                end_line=cls.end_line,
                                class_decorators=cls.class_decorators,
                                expressions=cls.expressions,
                                functions=[],
                            )
                            new_file_data.classes.append(new_class)

                        # 检查类中的函数
                        for func in cls.functions:
                            if func.start_line <= start_line <= func.end_line:
                                new_func_info = self._extract_text_in_range(
                                    func, start_line, end_line
                                )
                                new_class.functions.append(new_func_info)
                                matched = True
                                break  # 假设每个编辑只匹配一个函数
                        matched = True  # 已经匹配到了类，无论是否匹配到函数，都不需要继续检查其他类
                        break  # 假设每个编辑只匹配一个类

                if not matched:
                    # 检查顶级函数
                    for func in file_data.functions:
                        if func.start_line <= start_line <= func.end_line:
                            new_func_info = self._extract_text_in_range(
                                func, start_line, end_line
                            )
                            new_file_data.functions.append(new_func_info)
                            matched = True
                            break

                if not matched:
                    # 检查顶级表达式
                    for expr in file_data.top_level:
                        if expr.start_line <= start_line <= expr.end_line:
                            new_top_level = self._extract_text_in_range(
                                expr, start_line, end_line
                            )
                            new_file_data.top_level.append(new_top_level)
                            matched = True
                            break

                if not matched:
                    logger.debug(
                        f"在文件 {file_edits.file_name} 的行 {start_line}-{end_line} 未找到匹配的类或函数。"
                    )

            filtered_structure[file_edits.file_name] = new_file_data

        return filtered_structure

    def _extract_text_in_range(
        self, old_info: FunctionInfo, start_line: int, end_line: int
    ) -> FunctionInfo:
        """
        从旧的 FunctionInfo 中提取指定行范围的文本，保留 sketch，然后添加指定的代码行范围。
        同时更新 start_line、end_line 和 trimmed_code_start_line。
        """
        # 检查是否选中了整个函数
        if start_line == old_info.start_line and end_line == old_info.end_line:
            # 不需要截取，直接返回原始的 FunctionInfo
            return old_info

        lines = old_info.text.split("\n")
        section_start_line = old_info.start_line

        relative_start = max(0, start_line - section_start_line)
        relative_end = end_line - section_start_line + 1

        # 提取指定范围的代码行
        selected_lines = lines[relative_start:relative_end]

        # 保留 sketch
        if old_info.sketch:
            sketch_lines = old_info.sketch.split("\n")
            new_text = "\n".join(sketch_lines + selected_lines)
        else:
            new_text = "\n".join(selected_lines)

        # 保存选定代码的原始起始行号
        trimmed_code_start_line = start_line

        # 返回新的 FunctionInfo 对象
        return FunctionInfo(
            function_name=old_info.function_name,
            start_line=old_info.start_line,
            end_line=old_info.end_line,
            text=new_text,
            sketch=old_info.sketch,
            trimmed_code_start_line=trimmed_code_start_line,
        )
