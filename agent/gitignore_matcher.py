import os
import fnmatch
import time
import requests
from collections import defaultdict


class GitIgnoreMatcher:
    def __init__(self, gitignore_path=None, default_language="python"):
        """
        Initialize the GitIgnoreMatcher with optional path to the .gitignore file.
        Load and compile patterns from the .gitignore file.

        Args:
        gitignore_path (str): Path to the .gitignore file.
        default_language (str): Default language for the .gitignore file if not provided.
        """
        self.gitignore_path = gitignore_path
        self.default_language = default_language
        self.patterns = []
        self.neg_patterns = []
        self.pos_patterns = []
        self.pattern_cache = {}  # Cache for pattern matching results
        self.result_cache = {}  # Cache for is_ignored results
        self.dir_cache = set()  # Cache for directories to skip

    def load_gitignore_patterns(self, gitignore_path):
        """
        Load and parse patterns from the .gitignore file.

        Args:
        gitignore_path (str): Path to the .gitignore file.

        Returns:
        list: List of patterns from the .gitignore file.
        """
        print(f"Loading .gitignore patterns from file: {gitignore_path}")
        with open(gitignore_path, "r") as f:
            return [
                line.rstrip() for line in f if line.strip() and not line.startswith("#")
            ]

    def compile_patterns(self):
        """
        Compile patterns into categorized lists for efficient matching.
        """
        self.root_patterns = defaultdict(list)
        self.dir_patterns = []
        self.file_patterns = []

        for pattern in self.pos_patterns:
            if "/" in pattern:
                if pattern.startswith("/"):
                    root = pattern.split("/")[1]
                    self.root_patterns[root].append(pattern[1:])
                else:
                    self.dir_patterns.append(pattern)
            else:
                self.file_patterns.append(pattern)

    def match_pattern(self, path, pattern):
        """
        Match a path against a pattern, considering various special cases.

        Args:
        path (str): The path to match.
        pattern (str): The pattern to match against.

        Returns:
        bool: True if the path matches the pattern, False otherwise.
        """
        cache_key = (path, pattern)
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]

        result = False
        if pattern.startswith("/"):
            # Match patterns relative to the root directory
            result = fnmatch.fnmatch(path, pattern[1:])
        elif pattern.endswith("/"):
            # Match directories
            result = os.path.isdir(path) and fnmatch.fnmatch(path + "/", pattern)
        elif "**" in pattern:
            # Handle double asterisk patterns
            parts = pattern.split("**")
            result = path.startswith(parts[0]) and path.endswith(parts[-1])
        else:
            # Match regular patterns
            result = fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(
                os.path.basename(path), pattern
            )

        self.pattern_cache[cache_key] = result
        return result

    def is_ignored(self, path):
        """
        Check if a given path matches any ignore pattern.

        Args:
        path (str): The path to check.

        Returns:
        bool: True if the path is ignored, False otherwise.
        """
        if path in self.result_cache:
            return self.result_cache[path]

        rel_path = os.path.normpath(path)

        # Check negative patterns first
        for pattern in self.neg_patterns:
            if self.match_pattern(rel_path, pattern):
                self.result_cache[path] = False
                return False

        # Check root patterns
        root = rel_path.split(os.sep)[0]
        for pattern in self.root_patterns.get(root, []):
            if self.match_pattern(rel_path, pattern):
                self.result_cache[path] = True
                return True

        # Check directory patterns
        for pattern in self.dir_patterns:
            if self.match_pattern(rel_path, pattern):
                self.result_cache[path] = True
                return True

        # Check file patterns
        for pattern in self.file_patterns:
            if self.match_pattern(rel_path, pattern):
                self.result_cache[path] = True
                return True

        self.result_cache[path] = False
        return False

    def fetch_gitignore(self, language):
        """
        Fetch a .gitignore file for a specific language from the Toptal API.

        Args:
        language (str): The language for the .gitignore file.

        Returns:
        str: The path to the downloaded .gitignore file.
        """
        url = f"https://www.toptal.com/developers/gitignore/api/{language}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            gitignore_path = os.path.join(os.getcwd(), f"{language}.gitignore")
            with open(gitignore_path, "w") as f:
                f.write(response.text)
            print(f"Downloaded .gitignore file for {language} at {gitignore_path}")
            return gitignore_path
        except requests.RequestException as e:
            print(f"Failed to fetch .gitignore file for {language}: {e}")
            return None

    def check_directory(self, directory, language=None):
        """
        Check a directory and its contents against the ignore patterns.

        Args:
        directory (str): The directory to check.
        language (str): The language for the .gitignore file (optional).

        Returns:
        list: A list of paths that are not ignored.
        """
        if not self.patterns:
            if self.gitignore_path:
                self.patterns = self.load_gitignore_patterns(self.gitignore_path)
            else:
                gitignore_path = os.path.join(directory, ".gitignore")
                if not os.path.exists(gitignore_path):
                    gitignore_path = self.fetch_gitignore(
                        language or self.default_language
                    )
                if gitignore_path:
                    self.patterns = self.load_gitignore_patterns(gitignore_path)

            self.neg_patterns = [p[1:] for p in self.patterns if p.startswith("!")]
            self.pos_patterns = [p for p in self.patterns if not p.startswith("!")]
            self.compile_patterns()

        not_ignored = []
        print(f"Checking directory: {directory}")
        start_time = time.time()

        for entry in os.scandir(directory):
            if entry.is_dir(follow_symlinks=False):
                self.scan_directory(entry.path, not_ignored, directory)
            elif entry.is_file(follow_symlinks=False):
                rel_path = os.path.relpath(entry.path, directory)
                if not self.is_ignored(rel_path):
                    not_ignored.append(rel_path)
                else:
                    print(f"Path ignored: {rel_path}")

        end_time = time.time()
        print(f"Checked directory in {end_time - start_time:.4f} seconds")
        return not_ignored

    def scan_directory(self, dir_path, not_ignored, base_directory):
        """
        Recursively scan a directory and its contents against the ignore patterns.

        Args:
        dir_path (str): The path of the directory to scan.
        not_ignored (list): The list to store paths that are not ignored.
        base_directory (str): The base directory to calculate relative paths.
        """
        for entry in os.scandir(dir_path):
            rel_path = os.path.relpath(entry.path, base_directory)
            if entry.is_dir(follow_symlinks=False):
                if not self.is_ignored(rel_path):
                    self.scan_directory(entry.path, not_ignored, base_directory)
                else:
                    print(f"Directory ignored: {rel_path}")
            elif entry.is_file(follow_symlinks=False):
                if not self.is_ignored(rel_path):
                    not_ignored.append(rel_path)
                else:
                    print(f"Path ignored: {rel_path}")


# Example usage
if __name__ == "__main__":
    gitignore_path = None  # or provide a specific path
    matcher = GitIgnoreMatcher(gitignore_path)
    directory_to_check = '/path/to/check'  # replace with the actual directory path
    language = 'python'  # or the target language

    not_ignored_files = matcher.check_directory(directory_to_check, language)

    print("Files and directories not ignored:")
    for file in not_ignored_files:
        print(file)
