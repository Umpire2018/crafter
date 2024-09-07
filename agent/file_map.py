import os
import json
import pprint
import tree_sitter_python
from tree_sitter import Language, Parser, Node
from typing import List
from agent.schemas import (
    FileData,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    TopLevelInfo,
    ExpressionInfo,
    FileMapType,
    DecoratorInfo,
)
from dataclasses import dataclass
from pathlib import Path


# Initialize languages
LANGUAGE_MAP = {
    ".py": tree_sitter_python,
}


@dataclass
class MultiFileMap:
    file_dict: List[str]
    output_path: Path

    def save(self):
        """
        Generate the repository map by parsing all files in the file list and save to JSON.
        """
        all_file_data: FileMapType = {}  # 用于存储所有文件的数据

        for file_path in self.file_dict:
            # 清空单个文件映射的状态
            file_map = SingleFileMap(file_path)
            tree, source_code = file_map.parse_file()
            file_map.visit_node(tree.root_node, source_code)
            all_file_data[file_path] = file_map.data

        # 序列化所有数据并写入 JSON 文件
        json_content = json.dumps(
            {k: v.model_dump() for k, v in all_file_data.items()},
            ensure_ascii=False,
            indent=2,
        )

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(json_content)


class SingleFileMap:
    def __init__(self, file_path: str):
        """
        Initialize SingleFileMap with a file path.

        Args:
            file_path (str): Path to the file to be processed.
        """
        self.file_path = file_path
        self.parsers = {
            ext: Parser(Language(lang.language())) for ext, lang in LANGUAGE_MAP.items()
        }
        self.data = FileData()

    def parse_file(self) -> tuple[Node, bytes]:
        """
        Parse the file and return the syntax tree and source code.

        Returns:
            tuple[Node, bytes]: Syntax tree, source code.
        """
        ext = os.path.splitext(self.file_path)[1]
        if ext not in self.parsers:
            raise ValueError(f"Unsupported file extension: {ext}")

        with open(self.file_path, "r", encoding="utf-8") as file:
            source_code = file.read().encode("utf-8")

        parser = self.parsers[ext]
        tree = parser.parse(source_code)
        return tree, source_code

    def visit_node(self, node: Node, source_code: str):
        cursor = node.walk()

        while True:
            node_type = cursor.node.type

            if node_type in [
                "import_statement",
                "import_from_statement",
                "class_definition",
                "function_definition",
                "expression_statement",
                "if_statement",
            ]:
                if node_type in ["import_statement", "import_from_statement"]:
                    self.data.imports.append(
                        ImportInfo(
                            start_line=cursor.node.start_point[0] + 1,
                            end_line=cursor.node.end_point[0] + 1,
                            text=self.get_node_text(cursor.node, source_code),
                        )
                    )
                elif node_type in ["expression_statement", "if_statement"]:
                    self.data.top_level.append(
                        TopLevelInfo(
                            start_line=cursor.node.start_point[0] + 1,
                            end_line=cursor.node.end_point[0] + 1,
                            text=self.get_node_text(cursor.node, source_code),
                        )
                    )
                elif node_type == "class_definition":
                    self.process_class_definition(cursor.node, source_code)

                elif node_type == "function_definition":
                    self.process_function_definition(
                        cursor.node, source_code, top_level_or_not=True
                    )

                # 跳过子节点，直接处理兄弟节点
                if not cursor.goto_next_sibling():
                    # 如果没有更多兄弟节点，返回到父节点并继续
                    while not cursor.goto_parent():
                        return  # 无法返回父节点，结束遍历

                    # 继续到下一个兄弟节点
                    if not cursor.goto_next_sibling():
                        return  # 无法返回到兄弟节点且无法返回父节点，结束遍历

            else:
                if node_type not in ["module", "decorator", "decorated_definition"]:
                    pprint.pp(
                        f"{node_type} not supported yet, node_text:{self.get_node_text(cursor.node, source_code)}"
                    )
                # 处理非指定类型的节点，遍历子节点
                if cursor.goto_first_child():
                    continue  # 处理子节点
                while not cursor.goto_next_sibling():
                    # 如果没有更多兄弟节点，返回到父节点并继续
                    if not cursor.goto_parent():
                        return  # 无法返回到父节点，结束遍历

    def process_class_definition(self, class_node: Node, source_code: str):
        # 获取类名节点
        class_name_node = class_node.child_by_field_name("name")

        # 获取继承信息的 argument_list 节点
        superclass_node = class_node.child_by_field_name("superclasses")

        # 获取初始类名
        initial_class_name = self.get_node_text(class_name_node, source_code)

        # 检查并处理继承信息
        if superclass_node:
            # 初始化一个空列表来存储所有继承类的名字
            superclass_names = []
            # 遍历 argument_list 节点的所有子节点
            for child in superclass_node.children:
                if child.type == "identifier":
                    # 获取每个继承类的名字
                    superclass_name = self.get_node_text(child, source_code)
                    superclass_names.append(superclass_name)

            # 拼接类名和继承信息
            final_class_name = f"{initial_class_name}({', '.join(superclass_names)})"
        else:
            final_class_name = initial_class_name

        # 获取类的装饰器
        class_decorators = self.get_decorators(class_node, source_code)

        # 创建 ClassInfo 对象
        class_info = ClassInfo(
            class_name=final_class_name,
            class_decorators=class_decorators,
            start_line=class_decorators[-1].end_line + 1
            if class_decorators
            else class_name_node.start_point[0] + 1,
            end_line=class_node.end_point[0] + 1,
        )

        body_node = class_node.child_by_field_name("body")
        if body_node:
            for child in body_node.children:
                node_type = child.type
                if node_type == "expression_statement":
                    class_info.expressions.append(
                        ExpressionInfo(
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

        self.data.classes.append(class_info)

    def process_function_definition(
        self, function_node: Node, source_code: str, top_level_or_not: bool = False
    ):
        # Helper function to get docstring and comments
        def get_docstring_and_comments():
            # Extract the docstring from the function body
            body_node = function_node.child_by_field_name("body")
            docstring = None
            if body_node and body_node.child_count > 0:
                first_statement = body_node.child(0)
                if (
                    first_statement.type == "expression_statement"
                    and first_statement.child(0).type == "string"
                ):
                    docstring = self.get_node_text(
                        first_statement.child(0), source_code
                    )

            # Extract comments before the function definition
            comments = []
            for i in range(function_node.start_byte - 1, 0, -1):
                node = function_node.descendant_for_byte_range(i, i + 1)
                if node and node.type == "comment":
                    comments.insert(0, self.get_node_text(node, source_code))
                elif node and node.type != "comment":
                    break
            return docstring, comments

        # Helper function to process function parameters
        def process_parameters():
            parameters = []
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
            return parameters

        # Helper function to process the return type
        def process_return_type():
            return_type_node = function_node.child_by_field_name("return_type")
            return (
                self.get_node_text(return_type_node, source_code)
                if return_type_node
                else None
            )

        # Get function name
        function_name = self.get_node_text(
            function_node.child_by_field_name("name"), source_code
        )

        # Get docstring and comments
        docstring, comments = get_docstring_and_comments()

        # Process function parameters and return type
        parameters = process_parameters()
        return_type = process_return_type()

        # Get decorators (using DecoratorInfo model)
        decorators_info = self.get_decorators(function_node, source_code)
        # Extract decorator names
        decorators_str = (
            "\n".join(f"{decorator.decorator_name}" for decorator in decorators_info)
            + "\n"
            if decorators_info
            else ""
        )

        # Check if the function is asynchronous
        is_async = any(child.type == "async" for child in function_node.children)

        # Build sketch
        async_str = "async " if is_async else ""
        params_str = ", ".join(
            [f"{name}: {ptype}" if ptype else name for name, ptype in parameters]
        )
        return_str = f" -> {return_type}" if return_type else ""
        comments_str = "\n".join(comments) + "\n" if comments else ""
        docstring_str = f'\n    """{docstring}"""' if docstring else ""

        # Combine everything into the final sketch
        sketch = f"{comments_str}{decorators_str}{async_str}def {function_name}({params_str}){return_str}{docstring_str}"

        if top_level_or_not:
            self.data.functions.append(
                FunctionInfo(
                    function_name=function_name,
                    sketch=sketch,
                    start_line=function_node.start_point[0] + 1,
                    end_line=function_node.end_point[0] + 1,
                    text=self.get_node_text(function_node, source_code),
                )
            )
        else:
            return sketch, function_name

    def get_decorators(self, node: Node, source_code: str) -> list[DecoratorInfo]:
        """
        Get the decorators of a class or function.

        Args:
            node (Node): The class or function node.
            source_code (str): The source code of the file.

        Returns:
            list[DecoratorInfo]: List of DecoratorInfo objects with name and line numbers.
        """
        decorators = []
        if node.type == "decorated_definition":
            # Traverse children to find decorators in decorated_definition
            for child in node.children:
                if child.type == "decorator":
                    decorator_text = self.get_node_text(child, source_code)
                    decorators.append(
                        DecoratorInfo(
                            decorator_name=decorator_text,
                            start_line=child.start_point[0] + 1,
                            end_line=child.end_point[0] + 1,
                        )
                    )
        else:
            # Traverse previous siblings to find decorators for class
            current_node = node.prev_named_sibling
            while current_node:
                if current_node.type == "decorator":
                    decorator_text = self.get_node_text(current_node, source_code)
                    decorators.append(
                        DecoratorInfo(
                            decorator_name=decorator_text,
                            start_line=current_node.start_point[0] + 1,
                            end_line=current_node.end_point[0] + 1,
                        )
                    )
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
        "./RepoAgent/repo_agent/doc_meta_info.py",
        "./RepoAgent/repo_agent/runner.py",
        "./RepoAgent/repo_agent/utils/meta_info_utils.py",
        "./RepoAgent/repo_agent/exceptions.py",
        "./RepoAgent/repo_agent/settings.py",
        "agent/file_map.py",
    ]

    file_map = MultiFileMap(file_dict, output_path="repo_structure.json")
    file_map.save()
