import tree_sitter_python
import os
from tree_sitter import Language, Parser, Node
from collections import defaultdict

# Initialize languages
LANGUAGE_MAP = {
    ".py": tree_sitter_python,
}


class RepoMap:
    """Class to map the repository structure with classes, functions, and class attributes."""

    def __init__(self, file_dict: dict[str, dict[str, list[str] | None]]):
        """
        Initialize RepoMap with a dictionary of files, classes, and functions.

        Args:
            file_dict (dict[str, dict[str, list[str] | None]]): Dictionary with file paths as keys and
                a dictionary of classes and functions as values.
        """
        self.file_dict = file_dict
        self.repo_map = defaultdict(
            lambda: defaultdict(
                lambda: {"methods": [], "attributes": [], "class_decorators": []}
            )
        )
        self.parsers = {
            ext: Parser(Language(lang.language())) for ext, lang in LANGUAGE_MAP.items()
        }
        self.current_class = None

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

    def visit_node(self, node: Node, source_code: str, file_path):
        """
        Visit a node in the syntax tree and process class and function definitions.

        Args:
            node (Node): The current node to process.
            source_code (str): The source code of the file.
            file_path (str): The path of the file.
        """
        cursor = node.walk()

        while True:
            if cursor.node.type == "class_definition":
                class_name = self.get_node_text(
                    cursor.node.child_by_field_name("name"), source_code
                )
                if not class_name:
                    class_name = self.get_node_text(
                        cursor.node.child_by_field_name("identifier"), source_code
                    )
                self.current_class = class_name
                decorators = self.get_decorators(cursor.node, source_code)
                self.repo_map[file_path][self.current_class]["class_decorators"] = (
                    decorators
                )
                self.process_class_body(cursor.node, source_code, file_path)
            elif cursor.node.type == "function_definition" and not self.current_class:
                function_name = self.get_node_text(
                    cursor.node.child_by_field_name("name"), source_code
                )
                if not function_name:
                    function_name = self.get_node_text(
                        cursor.node.child_by_field_name("identifier"), source_code
                    )

                parameters, return_type = self.get_function_signature(
                    cursor.node, source_code
                )
                is_async = any(child.type == "async" for child in cursor.node.children)
                decorators = self.get_decorators(cursor.node, source_code)

                self.repo_map[file_path]["<top-level>"]["methods"].append(
                    (function_name, parameters, return_type, is_async, decorators)
                )

            if cursor.goto_first_child():
                continue
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    return

    def process_class_body(self, class_node: Node, source_code: str, file_path: str):
        """
        Process the body of a class to extract class attributes.

        Args:
            class_node (Node): The class node to process.
            source_code (str): The source code of the file.
            file_path (str): The path of the file.
        """
        body_node = class_node.child_by_field_name("body")
        if body_node:
            for child in body_node.children:
                if child.type == "expression_statement":
                    assignment = next(
                        (c for c in child.children if c.type == "assignment"), None
                    )
                    if assignment:
                        left = assignment.child_by_field_name("left")
                        right = assignment.child_by_field_name("right")
                        if left and right and left.type == "identifier":
                            attr_name = self.get_node_text(left, source_code)
                            attr_value = self.get_node_text(right, source_code)
                            self.repo_map[file_path][self.current_class][
                                "attributes"
                            ].append((attr_name, attr_value))
                elif child.type == "function_definition":
                    function_name = self.get_node_text(
                        child.child_by_field_name("name"), source_code
                    )
                    if not function_name:
                        function_name = self.get_node_text(
                            child.child_by_field_name("identifier"), source_code
                        )

                    parameters, return_type = self.get_function_signature(
                        child, source_code
                    )
                    is_async = any(c.type == "async" for c in child.children)
                    decorators = self.get_decorators(child, source_code)

                    self.repo_map[file_path][self.current_class]["methods"].append(
                        (function_name, parameters, return_type, is_async, decorators)
                    )
                elif child.type == "decorated_definition":
                    decorators = self.get_decorators(child, source_code)
                    for sub_child in child.children:
                        if sub_child.type == "function_definition":
                            function_name = self.get_node_text(
                                sub_child.child_by_field_name("name"), source_code
                            )
                            if not function_name:
                                function_name = self.get_node_text(
                                    sub_child.child_by_field_name("identifier"),
                                    source_code,
                                )
                            parameters, return_type = self.get_function_signature(
                                sub_child, source_code
                            )
                            is_async = any(
                                c.type == "async" for c in sub_child.children
                            )

                            self.repo_map[file_path][self.current_class][
                                "methods"
                            ].append(
                                (
                                    function_name,
                                    parameters,
                                    return_type,
                                    is_async,
                                    decorators,
                                )
                            )

    def get_function_signature(
        self, node: Node, source_code: str
    ) -> tuple[list[tuple[str, str]], str]:
        """
        Get the signature of a function including its parameters and return type.

        Args:
            node (Node): The function node.
            source_code (str): The source code of the file.

        Returns:
            tuple[list[tuple[str, str]], str]: List of parameters and their types, and the return type.
        """
        parameters = []
        return_type = None

        param_node = node.child_by_field_name("parameters")
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

        return_type_node = node.child_by_field_name("return_type")
        if return_type_node:
            return_type = self.get_node_text(return_type_node, source_code)

        return parameters, return_type

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

    def generate_repo_map(self):
        """
        Generate the repository map by parsing all files in the file list.
        """
        for file_path in self.file_dict.keys():
            tree, source_code = self.parse_file(file_path)
            self.visit_node(tree.root_node, source_code, file_path)

    def display_repo_map(self):
        """
        Display the repository map with class and function definitions.
        """
        for file_path, filter_dict in self.file_dict.items():
            if file_path in self.repo_map:
                print(f"{file_path}:")
                for class_name, class_info in self.repo_map[file_path].items():
                    if filter_dict is None or class_name in filter_dict:
                        decorators = class_info["class_decorators"]
                        decorator_str = "".join(
                            [f"{decorator}\n    " for decorator in decorators]
                        )
                        print(f"    {decorator_str}class {class_name}:")
                        for attr_name, attr_value in class_info["attributes"]:
                            print(f"        {attr_name} = {attr_value}")
                        for (
                            method,
                            parameters,
                            return_type,
                            is_async,
                            decorators,
                        ) in class_info["methods"]:
                            if (
                                filter_dict is None
                                or filter_dict.get(class_name) is None
                                or method in filter_dict.get(class_name, [])
                            ):
                                param_str = ", ".join(
                                    [
                                        f"{name}"
                                        if ptype is None
                                        else f"{name}: {ptype}"
                                        for name, ptype in parameters
                                    ]
                                )
                                return_str = f" -> {return_type}" if return_type else ""
                                async_str = "async " if is_async else ""
                                decorator_str = "".join(
                                    [
                                        f"{decorator}\n        "
                                        for decorator in decorators
                                    ]
                                )
                                print(
                                    f"        {decorator_str}{async_str}def {method}({param_str}){return_str}"
                                )
                    if "<top-level>" in (filter_dict or {}):
                        for (
                            method,
                            parameters,
                            return_type,
                            is_async,
                            decorators,
                        ) in self.repo_map[file_path]["<top-level>"]["methods"]:
                            if (
                                filter_dict is None
                                or filter_dict.get("<top-level>") is None
                                or method in filter_dict["<top-level>"]
                            ):
                                param_str = ", ".join(
                                    [
                                        f"{name}"
                                        if ptype is None
                                        else f"{name}: {ptype}"
                                        for name, ptype in parameters
                                    ]
                                )
                                return_str = f" -> {return_type}" if return_type else ""
                                async_str = "async " if is_async else ""
                                decorator_str = "".join(
                                    [f"@{decorator}\n    " for decorator in decorators]
                                )
                                print(
                                    f"    {decorator_str}{async_str}def {method}({param_str}){return_str}"
                                )


if __name__ == "__main__":
    # Example file list with classes and methods to filter
    file_dict = {
        "./RepoAgent/repo_agent/doc_meta_info.py": {
            "DocItem": None,
        },
        "agent/schemas.py": None,
    }

    repo_map = RepoMap(file_dict)
    repo_map.generate_repo_map()
    repo_map.display_repo_map()
