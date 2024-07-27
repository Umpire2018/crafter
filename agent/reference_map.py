import tree_sitter_python
import os
from tree_sitter import Language, Parser, Node
from collections import defaultdict

# Initialize languages
LANGUAGE_MAP = {
    ".py": tree_sitter_python,
}


class ReferenceMap:
    def __init__(self, file_list: list[str]):
        """
        Initialize ReferenceMap with a list of files.

        Args:
            file_list (list[str]): List of file paths to analyze.
        """
        self.file_list = file_list
        self.repo_map = defaultdict(lambda: defaultdict(list))
        self.parsers = {
            ext: Parser(Language(lang.language())) for ext, lang in LANGUAGE_MAP.items()
        }
        self.current_class = None

    def parse_file(self, file_path: str) -> tuple[Node, bytes]:
        ext = os.path.splitext(file_path)[1]
        if ext not in self.parsers:
            raise ValueError(f"Unsupported file extension: {ext}")

        with open(file_path, "r", encoding="utf-8") as file:
            source_code = file.read().encode("utf-8")
        parser = self.parsers[ext]
        tree = parser.parse(source_code)
        return tree, source_code

    def extract_references(self, node: Node, source_code: bytes):
        """
        Extract references from the given node.

        Args:
            node (Node): The root node to traverse.
            source_code (bytes): The source code in bytes.
        """

        def get_text(node):
            return source_code[node.start_byte : node.end_byte].decode("utf-8")

        def traverse(node, current_scope):
            if node.type == "function_definition":
                func_name = get_text(node.child_by_field_name("name"))
                current_scope.append(func_name)
                self.repo_map[current_scope[0]]["functions"].append(func_name)
            elif node.type == "class_definition":
                class_name = get_text(node.child_by_field_name("name"))
                current_scope.append(class_name)
                self.repo_map[class_name]["classes"].append(class_name)
                self.current_class = class_name
            elif node.type == "call":
                func_name = get_text(node.child_by_field_name("function"))
                if self.current_class:
                    self.repo_map[self.current_class]["calls"].append(func_name)
                else:
                    self.repo_map[current_scope[0]]["calls"].append(func_name)

            for child in node.children:
                traverse(child, current_scope)
            if node.type in ["function_definition", "class_definition"]:
                current_scope.pop()

        traverse(node, [])

    def analyze_repo(self):
        """
        Analyze the repository to extract references.
        """
        for file_path in self.file_list:
            tree, source_code = self.parse_file(file_path)
            self.extract_references(tree.root_node, source_code)

    def display_references(self):
        """
        Display the extracted references in a developer-friendly way.
        """
        for key, value in self.repo_map.items():
            print(f"{key}:")
            if "classes" in value:
                print(f"  Classes:")
                for cls in value["classes"]:
                    print(f"    {cls}")
            if "functions" in value:
                print(f"  Functions:")
                for func in value["functions"]:
                    print(f"    {func}")
            if "calls" in value:
                print(f"  Calls:")
                for call in value["calls"]:
                    print(f"    {call}")


if __name__ == "__main__":
    # Example usage
    file_list = ["agent/llm_initializer.py", "agent/test.py"]
    reference_map = ReferenceMap(file_list)
    reference_map.analyze_repo()
    reference_map.display_references()
