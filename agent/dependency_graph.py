import os
import ast
from collections import defaultdict


class DependencyGraph:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.file_list = self.collect_files()
        self.dependency_graph = defaultdict(list)
        self.build_dependency_graph()

    def collect_files(self) -> list[str]:
        """
        Collect all Python files in the project directory.
        """
        python_files = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    python_files.append(full_path)
        return python_files

    def parse_imports(self, file_path: str) -> list[str]:
        """
        Parse the imports from a Python file.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            node = ast.parse(file.read(), filename=file_path)

        imports = []
        for n in ast.walk(node):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    imports.append(alias.name)
            elif isinstance(n, ast.ImportFrom):
                module = n.module
                if module:
                    imports.append(module)
        return imports

    def build_dependency_graph(self):
        """
        Build the dependency graph for the project.
        """
        for file_path in self.file_list:
            relative_path = os.path.relpath(file_path, self.project_root)
            imports = self.parse_imports(file_path)
            for imp in imports:
                self.dependency_graph[imp].append(relative_path)

    def find_references(self, target_file: str) -> list[str]:
        """
        Find all files that reference the target file.
        """
        references = []
        target_module = os.path.splitext(target_file.replace(os.sep, "."))[0]
        for module, files in self.dependency_graph.items():
            if target_module.endswith(module):
                references.extend(files)
        return references

    def display_dependencies(self):
        """
        Display the dependency graph.
        """
        for module, files in self.dependency_graph.items():
            print(f"{module}:")
            for file in files:
                print(f"  {file}")


if __name__ == "__main__":
    project_root = "agent"
    target_file = "agent/test.py"
    graph = DependencyGraph(project_root)
    graph.display_dependencies()

    references = graph.find_references(target_file)
    print(f"Files referencing {target_file}:")
    for ref in references:
        print(f"  {ref}")
