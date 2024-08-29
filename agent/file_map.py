import os
import json
import tree_sitter_python
from tree_sitter import Language, Parser, Node
from typing import List
from agent.schema import (
    FileData,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    Expressioninfo,
    FileMapType,
)

# Initialize languages
LANGUAGE_MAP = {
    ".py": tree_sitter_python,
}


class FileMap:
    def __init__(self, file_dict: List[str] | None):
        """
        Initialize FileMap with a dictionary of files, classes, and functions.

        Args:
            file_dict (dict[str, dict[str, list[str] | None]]): Dictionary with file paths as keys and
                a dictionary of classes and functions as values.
        """
        self.file_dict = file_dict
        self.parsers = {
            ext: Parser(Language(lang.language())) for ext, lang in LANGUAGE_MAP.items()
        }
        self.function_name = None

    def parse_file(self, file_path: str) -> tuple[Node, bytes]:
        """
        Parse a file and return the syntax tree, source code.

        Args:
            file_path (str): Path to the file to parse.

        Returns:
            tuple[Node, bytes]: Syntax tree, source code.
        """
        ext = os.path.splitext(file_path)[1]
        if ext not in self.parsers:
            raise ValueError(f"Unsupported file extension: {ext}")

        with open(file_path, "r", encoding="utf-8") as file:
            source_code = file.read().encode("utf-8")

        parser = self.parsers[ext]
        tree = parser.parse(source_code)
        return tree, source_code

    def save(self, output_path):
        """
        Generate the repository map by parsing all files in the file list and save to JSON.

        Args:
            output_path (str): Path to save the JSON file.
        """
        all_file_data: FileMapType = {}  # 用于存储所有文件的数据

        for file_path in self.file_dict:
            try:
                tree, source_code = self.parse_file(file_path)
                file_data = self.visit_node(tree.root_node, source_code)
                all_file_data[file_path] = file_data  # 将结果存入字典中

            except Exception as e:
                print(f"Error parsing {file_path}: {e}")

        # 序列化所有数据并写入 JSON 文件
        json_content = json.dumps(
            {k: v.model_dump() for k, v in all_file_data.items()},
            ensure_ascii=False,
            indent=2,
        )

        with open(output_path, "w", encoding="utf-8") as json_file:
            json_file.write(json_content)

    def visit_node(self, node: Node, source_code: str):
        cursor = node.walk()
        highest_end_line = 0
        file_data = FileData()

        while True:
            node_type = cursor.node.type
            current_end_line = cursor.node.end_point[0]

            if node_type in [
                "import_statement",
                "import_from_statement",
                "class_definition",
                "function_definition",
            ]:
                if current_end_line < highest_end_line:
                    if not cursor.goto_next_sibling():
                        break
                    continue

                if node_type in ["import_statement", "import_from_statement"]:
                    file_data.imports.append(
                        ImportInfo(
                            start_line=cursor.node.start_point[0] + 1,
                            end_line=current_end_line + 1,
                            text=self.get_node_text(cursor.node, source_code),
                        )
                    )

                elif node_type == "class_definition":
                    class_data = self.process_class_definition(cursor.node, source_code)
                    file_data.classes.append(class_data)

                elif node_type == "function_definition":
                    self.process_function_definition(cursor.node, source_code)

                highest_end_line = current_end_line

            if cursor.goto_first_child():
                continue
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    return

        return file_data

    def process_class_definition(self, class_node: Node, source_code: str):
        class_name = self.get_node_text(
            class_node.child_by_field_name("name"), source_code
        )

        class_decorators = self.get_decorators(class_node, source_code)

        class_info = ClassInfo(
            class_name=class_name,
            class_decorators=class_decorators,
        )

        body_node = class_node.child_by_field_name("body")
        if body_node:
            for child in body_node.children:
                node_type = child.type
                if node_type == "expression_statement":
                    class_info.expressions.append(
                        Expressioninfo(
                            start_line=child.start_point[0] + 1,
                            end_line=child.end_point[0] + 1,
                            text=self.get_node_text(child, source_code),
                        )
                    )
                elif node_type in ["function_definition", "decorated_definition"]:
                    if node_type == "function_definition":
                        sketch, function_name = self.process_function_definition(
                            child, source_code
                        )

                    elif node_type == "decorated_definition":
                        for sub_child in child.children:
                            if sub_child.type == "function_definition":
                                sketch, function_name = (
                                    self.process_function_definition(
                                        sub_child, source_code
                                    )
                                )

                    function_info = FunctionInfo(
                        function_name=function_name,
                        sketch=sketch,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        text=self.get_node_text(child, source_code),
                    )
                    class_info.functions.append(function_info)

        return class_info

    def process_function_definition(self, function_node: Node, source_code: str):
        function_name = self.get_node_text(
            function_node.child_by_field_name("name"), source_code
        )

        # 检查函数是否已处理过（用于避免重复处理内容为 "pass" 的函数）
        if function_name == self.function_name:
            return
        self.function_name = function_name

        parameters = []
        return_type = None
        param_node = function_node.child_by_field_name("parameters")
        if param_node:
            for param in param_node.children:
                param_name = None
                param_type = None

                if param.type == "identifier" and not param.children:
                    param_name = self.get_node_text(param, source_code)
                    parameters.append((param_name, param_type))
                elif param.type == "typed_parameter":
                    for child in param.children:
                        if child.type == "identifier":
                            param_name = self.get_node_text(child, source_code)
                        elif child.type == "type":
                            param_type = self.get_node_text(child, source_code)
                    if param_name:
                        parameters.append((param_name, param_type))

        return_type_node = function_node.child_by_field_name("return_type")
        if return_type_node:
            return_type = self.get_node_text(return_type_node, source_code)

        decorators = self.get_decorators(function_node, source_code)

        # 检查函数是否为异步
        is_async = any(child.type == "async" for child in function_node.children)

        # 构建 sketch
        indent_str = " " * 2
        async_str = "async " if is_async else ""
        params_str = ", ".join(
            [f"{name}: {ptype}" if ptype else name for name, ptype in parameters]
        )
        return_str = f" -> {return_type}" if return_type else ""
        decorators_str = (
            "\n".join(f"{indent_str}{decorator}" for decorator in decorators)
            if decorators
            else ""
        )
        sketch = f"{decorators_str}\n{indent_str}{async_str}def {function_name}({params_str}){return_str}"

        return sketch, function_name

    def get_decorators(self, node: Node, source_code: str) -> list[str]:
        """
        Get the decorators of a class or function.

        Args:
            node (Node): The class or function node.
            source_code (str): The source code of the file.

        Returns:
            list[str]: List of decorators.
        """
        decorators = []
        if node.type == "decorated_definition":
            # Traverse children to find decorators in decorated_definition
            for child in node.children:
                if child.type == "decorator":
                    decorator_text = self.get_node_text(child, source_code)
                    decorators.append(decorator_text)
        else:
            # Traverse previous siblings to find decorators for class
            current_node = node.prev_named_sibling
            while current_node:
                if current_node.type == "decorator":
                    decorator_text = self.get_node_text(current_node, source_code)
                    decorators.append(decorator_text)
                current_node = current_node.prev_named_sibling
            decorators.reverse()  # Reverse to maintain the correct order

        return decorators

    def get_node_text(self, node: Node, source_code: bytes) -> str:
        """
        Get the text content of a node.

        Args:
            node (Node): The node to get text from.
            source_code (bytes): The source code of the file.

        Returns:
            str: The text content of the node.
        """
        return (
            source_code[node.start_byte : node.end_byte].decode("utf-8") if node else ""
        )

    def get_text_by_relative_line(
        self, file_path: str, section: str, relative_line: int
    ) -> str:
        """
        Get the content of a specific relative line in a given section of a file.

        Args:
            file_path (str): Path of the file.
            section (str): Section type ("Imports", "Classes", "Top level").
            relative_line (int): Relative line number within the section.

        Returns:
            str: Content of the specified line.
        """
        if file_path not in self.file_data:
            raise ValueError(f"File {file_path} not found.")
        if section not in self.file_data[file_path]:
            raise ValueError(f"Section {section} not found in file {file_path}.")
        if not (0 <= relative_line < len(self.file_data[file_path][section])):
            raise IndexError(
                f"Relative line {relative_line} is out of range for section {section} in file {file_path}."
            )

        return self.file_data[file_path][section][relative_line]["text"][relative_line]


if __name__ == "__main__":
    # Example file list with classes and methods to filter
    file_dict = [
        # "./RepoAgent/repo_agent/doc_meta_info.py",
        # "./RepoAgent/repo_agent/runner.py",
        # "./RepoAgent/repo_agent/utils/meta_info_utils.py",
        # "./RepoAgent/repo_agent/exceptions.py",
        # "./RepoAgent/repo_agent/settings.py",
        "agent/schemas.py",
    ]

    file_map = FileMap(file_dict)
    file_map.save("repo_structure.json")
