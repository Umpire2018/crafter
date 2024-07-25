import tree_sitter_python
import os
from tree_sitter import Language, Parser, Node
from collections import defaultdict

# Initialize languages
LANGUAGE_MAP = {
    '.py': tree_sitter_python,
}

class RepoMap:
    """Class to map the repository structure with classes and functions."""
    
    def __init__(self, file_list: list[str]):
        """
        Initialize RepoMap with a list of files.
        
        Args:
            file_list (list[str]): List of file paths to analyze.
        """
        self.file_list = file_list
        self.repo_map = defaultdict(lambda: defaultdict(list))
        self.parsers = {ext: Parser(Language(lang.language())) for ext, lang in LANGUAGE_MAP.items()}
        self.current_class = None 

    def parse_file(self, file_path: str) -> tuple[Node, bytes, str]:
        """
        Parse a file and return the syntax tree, source code, and file extension.
        
        Args:
            file_path (str): Path to the file to parse.
        
        Returns:
            tuple[Node, bytes, str]: Syntax tree, source code, and file extension.
        """
        ext = os.path.splitext(file_path)[1]
        if ext not in self.parsers:
            raise ValueError(f'Unsupported file extension: {ext}')
        
        with open(file_path, 'r', encoding='utf-8') as file:
            source_code = file.read().encode('utf-8')
        parser = self.parsers[ext]
        tree = parser.parse(source_code)
        return tree, source_code, ext

    def visit_node(self, node: Node, source_code: str, file_path, ext):
        """
        Visit a node in the syntax tree and process class and function definitions.
        
        Args:
            node (Node): The current node to process.
            source_code (str): The source code of the file.
            file_path (str): The path of the file.
            ext (str): The file extension.
        """
        cursor = node.walk()

        while True:
            if cursor.node.type == 'class_definition':
                class_name = self.get_node_text(cursor.node.child_by_field_name('name'), source_code)
                if not class_name:
                    class_name = self.get_node_text(cursor.node.child_by_field_name('identifier'), source_code)
                self.current_class = class_name
            elif cursor.node.type == 'function_definition':
                function_name = self.get_node_text(cursor.node.child_by_field_name('name'), source_code)
                if not function_name:
                    function_name = self.get_node_text(cursor.node.child_by_field_name('identifier'), source_code)
                
                parameters, return_type = self.get_function_signature(cursor.node, source_code)
                is_async = any(child.type == 'async' for child in cursor.node.children)

                if self.current_class:
                    self.repo_map[file_path][self.current_class].append((function_name, parameters, return_type, is_async))
                else:
                    self.repo_map[file_path]['<top-level>'].append((function_name, parameters, return_type, is_async))

            if cursor.goto_first_child():
                continue
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    return

    def get_function_signature(self, node: Node, source_code: str) -> tuple[list[tuple[str, str]], str]:
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

        param_node = node.child_by_field_name('parameters')
        if param_node:
            for param in param_node.children:
                param_name = None
                param_type = None

                if param.type == 'identifier' and not param.children:
                    param_name = self.get_node_text(param, source_code)
                    parameters.append((param_name, param_type))
                elif param.type == 'typed_parameter':
                    for child in param.children:
                        if child.type == 'identifier':
                            param_name = self.get_node_text(child, source_code)
                        elif child.type == 'type':
                            param_type = self.get_node_text(child, source_code)
                    if param_name:
                        parameters.append((param_name, param_type))

        return_type_node = node.child_by_field_name('return_type')
        if return_type_node:
            return_type = self.get_node_text(return_type_node, source_code)

        return parameters, return_type

    def get_node_text(self, node: Node, source_code: bytes) -> str:
        """
        Get the text content of a node.
        
        Args:
            node (Node): The node to get text from.
            source_code (bytes): The source code of the file.
        
        Returns:
            str: The text content of the node.
        """
        if node is not None:
            text = source_code[node.start_byte:node.end_byte].decode('utf-8')
            return text
        return ''

    def generate_repo_map(self):
        """
        Generate the repository map by parsing all files in the file list.
        """
        for file_path in self.file_list:
            tree, source_code, ext = self.parse_file(file_path)
            self.visit_node(tree.root_node, source_code, file_path, ext)

    def display_repo_map(self):
        """
        Display the repository map with class and function definitions.
        """
        for file_path, classes in self.repo_map.items():
            print(f'{file_path}:')
            for class_name, methods in classes.items():
                print(f'  class {class_name}:')
                for method, parameters, return_type, is_async in methods:
                    param_str = ', '.join([f'{name}' if ptype is None else f'{name}: {ptype}' for name, ptype in parameters])
                    return_str = f' -> {return_type}' if return_type else ''
                    async_str = 'async ' if is_async else ''
                    print(f'    {async_str}def {method}({param_str}){return_str}')

if __name__ == "__main__":
    # 示例文件列表
    file_list = [
        "agent/test.py",
        "agent/repo_map.py",
    ]

    repo_map = RepoMap(file_list)
    repo_map.generate_repo_map()
    repo_map.display_repo_map()
