from regex import P
import tree_sitter_python
import os
from tree_sitter import Language, Parser, Node
from collections import defaultdict
from typing import Dict, List


# Initialize languages
LANGUAGE_MAP = {
    ".py": tree_sitter_python,
}


class RepoMap:
    """Class to map the repository structure with classes, functions, and class attributes."""

    def __init__(self, file_dict: List[str] | None):
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
        self.imports = defaultdict(lambda:{})
        self.parsers = {
            ext: Parser(Language(lang.language())) for ext, lang in LANGUAGE_MAP.items()
        }
        self.current_class = None
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
    
    def visit_node(self, node: Node, source_code: str, file_path: str):
        """
        Traverse the node and process class, function definitions and their internal contents.

        Args:
            node (Node): Current node.
            source_code (str): Source code of the file.
            file_path (str): Path of the file.
        """
        cursor = node.walk()
        highest_end_line = 0
        current_end_line = 0

        while True:
            node_type = cursor.node.type
            current_end_line, current_end_column = cursor.node.end_point

            if node_type in ["import_statement", "import_from_statement", "class_definition", "function_definition"]: 

                if current_end_line < highest_end_line:
                    if not cursor.goto_next_sibling():
                        break
                    continue

                # print(f"current_end_line: {current_end_line}, highest_end_line: {highest_end_line}, curren_node_type: {node_type}, current_end_column: {current_end_column}")
                
                if node_type in ["import_statement", "import_from_statement"]:
                    self.process_import_statement(cursor.node, source_code, file_path)
                elif node_type == "class_definition":
                    self.process_class_definition(cursor.node, source_code, file_path)
                elif node_type == "function_definition":
                    self.process_function_definition(cursor.node, source_code, file_path)

                highest_end_line = current_end_line

            if cursor.goto_first_child():
                continue
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    return

    def process_class_definition(self, class_node: Node, source_code: str, file_path: str):
        self.class_name = self.get_node_text(
                    class_node.child_by_field_name("name"), source_code
                )
        print(f"Class Name: {self.class_name}")

        class_decorators = self.get_decorators(class_node, source_code)
        self.repo_map[file_path][self.class_name]["class_decorators"] = class_decorators

        body_node = class_node.child_by_field_name("body")
        if body_node:
            for child in body_node.children:
                if child.type == "expression_statement":
                    self.process_expression_statement(child, source_code, file_path)
                elif child.type == "function_definition":
                    self.process_function_definition(child, source_code, file_path)
                elif child.type == "decorated_definition":
                    self.process_decorated_definition(child, source_code, file_path)
                    
        self.class_name = None


    def process_function_definition(self, function_node: Node, source_code: str, file_path: str, decorators=None):
        parameters, return_type = self.get_function_signature(function_node, source_code)
        is_async = any(child.type == "async" for child in function_node.children)
        if decorators is None:
            decorators = self.get_decorators(function_node, source_code)

        function_name = self.get_node_text(function_node.child_by_field_name("name"), source_code)

        # NOTE: Add self.function_name to check if the function is already processed to avoid when the content of function is "pass", then endline is equal to class endline, which will be processed again.
        if function_name == self.function_name:
            return
        self.function_name = function_name

        if self.class_name:
            self.repo_map[file_path][self.class_name]["methods"].append(
                (function_name, parameters, return_type, is_async, decorators)
            )
        else:
            self.repo_map[file_path]["<top-level>"]["methods"].append(
                (function_name, parameters, return_type, is_async, decorators)
            )

    def process_expression_statement(self, expr_node: Node, source_code: str, file_path: str):
        """
        Process an expression statement node.

        Args:
            expr_node (Node): The expression statement node to process.
            source_code (str): The source code of the file.
            file_path (str): The path of the file.
        """
        assignment = next((c for c in expr_node.children if c.type == "assignment"), None)
        if assignment:
            left = assignment.child_by_field_name("left")
            right = assignment.child_by_field_name("right")
            if left and right and left.type == "identifier":
                attr_name = self.get_node_text(left, source_code)
                attr_value = self.get_node_text(right, source_code)
                if self.class_name:
                    self.repo_map[file_path][self.class_name]["attributes"].append((attr_name, attr_value))
                else:
                    self.repo_map[file_path]["attributes"].append((attr_name, attr_value))

    def process_decorated_definition(self, decorated_node: Node, source_code: str, file_path: str):
        """
        Process a decorated definition node.

        Args:
            decorated_node (Node): The decorated definition node to process.
            source_code (str): The source code of the file.
            file_path (str): The path of the file.
        """
        decorators = self.get_decorators(decorated_node, source_code)
        for sub_child in decorated_node.children:
            if sub_child.type == "function_definition":
                self.process_function_definition(sub_child, source_code, file_path, decorators)


    def process_import_statement(self, node, source_code, file_path):
        """
        Process an import statement and update the import_statements dictionary.

        Args:
            node (Node): The import statement node.
            source_code (str): The source code of the file.
            file_path (str): Path of the file.
        """
        import_statements = self.imports[file_path]

        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    module_name = self.get_node_text(child, source_code)
                    import_statements[module_name] = None
                elif child.type == "aliased_import":
                    module_name = self.get_node_text(child.child_by_field_name("name"), source_code)
                    alias_name = self.get_node_text(child.child_by_field_name("alias"), source_code)
                    import_statements[alias_name] = module_name
        
        elif node.type == "import_from_statement":
            module_name = ""
            for child in node.children:
                if child.type == "dotted_name":
                    if not module_name:
                        module_name = self.get_node_text(child, source_code)
                        import_statements[module_name] = import_statements.get(module_name, [])
                    else:
                        import_statements[module_name].append(self.get_node_text(child, source_code))
                elif child.type == "import_list":
                    for name in child.named_children:
                        import_statements[module_name].append(self.get_node_text(name, source_code))

    def is_imported(self, call_name, import_statements):
        """
        Check if a call name is part of the imported statements.

        Args:
            call_name (str): The name of the function being called.
            import_statements (dict): Dictionary of import statements.

        Returns:
            bool: True if the call name is part of the imported statements, False otherwise.
        """
        for alias, module in import_statements.items():
            if call_name == alias or call_name.startswith(f"{alias}."):
                return True
            if module and (call_name == module or call_name.startswith(f"{module}.")):
                return True
        return False

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
        for file_path in self.file_dict:
            try:
                tree, source_code = self.parse_file(file_path)
                self.visit_node(tree.root_node, source_code, file_path)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")

        print(f"Original Import map: {self.imports}")
        
        # Printing the repository map in the desired format
        for file_path, classes in self.repo_map.items():
            print(f"{file_path}:")

            if file_path in self.imports:
                print("  Imports:")
                for module_name, imported_names in self.imports[file_path].items():
                    if imported_names is None:
                        print(f"    import {module_name}")
                    elif imported_names:
                        if len(imported_names) == 1:
                            print(f"    from {module_name} import {imported_names[0]}")
                        else:
                            imports_str = ", ".join(imported_names)
                            print(f"    from {module_name} import {imports_str}")

            for class_name, class_contents in classes.items():
                if class_name == "<top-level>":
                    print("  <top-level>:")
                    self.print_methods(class_contents["methods"], indent=4)
                else:
                    class_decorators = class_contents["class_decorators"]
                    if class_decorators:
                        for decorator in class_decorators:
                            print(f"  {decorator}")
                    print(f"  class {class_name}:")
                    self.print_attributes(class_contents["attributes"], indent=4)
                    self.print_methods(class_contents["methods"], indent=4)
            print("")  # Add a blank line between files for readability

    def print_methods(self, methods, indent=2):
        """
        Print the methods in the desired format.

        Args:
            methods (list): List of methods to print.
            indent (int): Indentation level.
        """
        indent_str = ' ' * indent
        for method in methods:
            method_name, parameters, return_type, is_async, decorators = method
            async_str = "async " if is_async else ""
            params_str = ", ".join([f"{name}: {ptype}" if ptype else name for name, ptype in parameters])
            return_str = f" -> {return_type}" if return_type else ""
            if decorators:
                for decorator in decorators:
                    print(f"{indent_str}{decorator}")
            print(f"{indent_str}{async_str}def {method_name}({params_str}){return_str}")

    def print_attributes(self, attributes, indent=4):
        """
        Print the class attributes in the desired format.

        Args:
            attributes (list): List of attributes to print.
            indent (int): Indentation level.
        """
        indent_str = ' ' * indent
        for attr_name, attr_value in attributes:
            print(f"{indent_str}{attr_name} = {attr_value}")

if __name__ == "__main__":
    # Example file list with classes and methods to filter
    file_dict = [
        "./RepoAgent/repo_agent/doc_meta_info.py",
        "./RepoAgent/repo_agent/runner.py", 
        "./RepoAgent/repo_agent/utils/meta_info_utils.py", 
        "./RepoAgent/repo_agent/exceptions.py", 
        "./RepoAgent/repo_agent/settings.py",
        # "agent/test.py",
    ]

    repo_map = RepoMap(file_dict)
    repo_map.generate_repo_map()
