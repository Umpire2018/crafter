import os


class DirectoryTreePrinter:
    def __init__(self, directory_to_check, target_language="python"):
        """
        Initialize the DirectoryTreePrinter class.

        Args:
            directory_to_check (str): The directory to check.
            target_language (str): The target programming language.
        """
        self.directory_to_check = directory_to_check
        self.target_language = target_language
        self.language_extensions = self.get_language_extensions()

    def get_language_extensions(self):
        """
        Get file extensions for the target programming language.

        Returns:
            list: A list of file extensions.
        """
        language_extensions = {
            "python": [".py"],
            "java": [".java"],
            "javascript": [".js"],
            "c++": [".cpp", ".h"],
            # Add more languages and their file extensions here
        }
        return language_extensions.get(self.target_language, [])

    def add_to_tree(self, tree, parts):
        """
        Add file parts to the directory tree.

        Args:
            tree (dict): The directory tree.
            parts (list): The parts of the file path.
        """
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = None

    def print_tree_helper(self, tree, prefix=""):
        """
        Recursively print the directory tree.

        Args:
            tree (dict): The directory tree.
            prefix (str): The prefix for each line of the tree.
        """
        items = sorted(tree.items())
        for i, (name, subtree) in enumerate(items):
            is_last = i == len(items) - 1
            print(f"{prefix}{'└── ' if is_last else '├── '}{name}")
            if subtree is not None:
                extension = "    " if is_last else "│   "
                self.print_tree_helper(subtree, prefix + extension)

    def filter_and_convert_files(self, file_list):
        """
        Filter and convert file paths based on the target language extensions.

        Args:
            file_list (list): The list of files.

        Returns:
            list: A list of filtered and converted file paths.
        """
        filtered_files = []
        for file in file_list:
            if os.path.splitext(file)[1] in self.language_extensions:
                relative_path = os.path.relpath(
                    os.path.join(self.directory_to_check, file), self.directory_to_check
                )
                parts = relative_path.split(os.sep)
                filtered_files.append(parts)
        return filtered_files

    def print_tree(self, file_list):
        """
        Print the directory tree for the given file list.

        Args:
            file_list (list): The list of files.
        """
        filtered_files = self.filter_and_convert_files(file_list)
        file_tree = {}
        for parts in filtered_files:
            self.add_to_tree(file_tree, parts)

        print(f"{os.path.basename(self.directory_to_check)}")
        self.print_tree_helper(file_tree, "")


if __name__ == "__main__":
    import time

    directory_to_check = "./directory_to_check"
    language = "python"  # or the target language

    start_time = time.time()
    tree_printer = DirectoryTreePrinter(directory_to_check, target_language=language)
    end_time = time.time()

    not_ignored_files = [
        "test.py",
    ]

    tree_printer.print_tree(not_ignored_files)
    print(f"Printed Tree structure in {end_time - start_time:.4f} seconds")