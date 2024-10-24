from llama_index.core import PromptTemplate

regenerate_git_diff_prompt_str = (
    "Please analyze the following original source code and the instructions for code modifications. Based on the provided modification instructions, identify the specific lines that need to be changed. Only include the lines that require changes. If a modification involves a single line, provide that line number; if it involves multiple lines, provide the range of lines. Present the differences in a structured JSON format suitable for programmatic processing. For each modification, include the following details:\n"
    "- **file_path**: The path to the file that needs modification.\n"
    "- **changes**: A list of changes, each containing:\n"
    "  - **start_line**: The starting line number.\n"
    "  - **end_line**: The ending line number. If it's a single line, start_line and end_line are the same.\n"
    "  - **original_code**: The original code that needs modification (corresponding to the line numbers).\n"
    "  - **modified_code**: The modified code.\n"
    "Ensure that the JSON is properly formatted and that any special characters in strings are correctly escaped to prevent parsing errors.\n\n"
    "### Original Source Code:\n"
    "{source_code}\n\n"
    "### Instructions for Code Modifications:\n"
    "{modification_instructions}\n\n"
    "### Required JSON Format:\n"
    "```\n"
    "{{\n"
    "  \"modifications\": [\n"
    "    {{\n"
    "      \"file_path\": \"./path/to/file.py\",\n"
    "      \"changes\": [\n"
    "        {{\n"
    "          \"start_line\": starting line number,\n"
    "          \"end_line\": ending line number,\n"
    "          \"original_code\": \"original code\",\n"
    "          \"modified_code\": \"modified code\"\n"
    "        }},\n"
    "        ...\n"
    "      ]\n"
    "    }},\n"
    "    ...\n"
    "  ]\n"
    "}}\n"
    "```\n"
    "Please provide the differences in this JSON format, including only the specific lines that need to be changed. If a modification involves multiple lines, provide the corresponding line range.\n"
)


regenerate_git_diff_template = PromptTemplate(regenerate_git_diff_prompt_str)

test_regenerate_git_diff_output = {
  "modifications": [
    {
      "file_path": "./RepoAgent/repo_agent/doc_meta_info.py",
      "changes": [
        {
          "start_line": 158,
          "end_line": 171,
          "original_code": [
            "def check_depth(self):\n",
            "        if len(self.children) == 0:\n",
            "            self.depth = 0\n",
            "            return self.depth\n",
            "        max_child_depth = 0\n",
            "        for _, child in self.children.items():\n",
            "            child_depth = child.check_depth()\n",
            "            max_child_depth = max(child_depth, max_child_depth)\n",
            "        self.depth = max_child_depth + 1\n",
            "        return self.depth"
          ],
          "modified_code": [
            "def check_depth(self):\n",
            "        if len(self.children) == 0:\n",
            "            self.depth = 0\n",
            "            return self.depth\n",
            "        # Ensure that the recursive call is reducing the problem size\n",
            "        max_child_depth = max(child.check_depth() for child in self.children)\n",
            "        self.depth = max_child_depth + 1\n",
            "        return self.depth"
          ]
        }
      ]
    }
  ]
}