from llama_index.core import PromptTemplate

generate_git_diff_prompt_str = (
    "Please analyze the following problem description and the identified source code snippet for the repository named {target_repository_name} "
    "which primarily uses the {main_language} language. The snippet below has already been identified as the relevant code to be modified. "
    "Based on the problem description, generate the necessary changes to the code in git diff format.\n"
    "## Relevant Algorithm to solve the next problem: {retrieved_algorithm}"
    "### Problem Description\n"
    "{problem_description}\n"
    "### Identified Source Code Snippet\n"
    "{source_code}\n"
    "## Planning:\n"
    "{planning_of_problem}\n"
    "### Return the modifications in the following git diff format:\n"
    "```\n"
    "diff --git a/path/to/file.py b/path/to/file.py\n"
    "--- a/path/to/file.py\n"
    "+++ b/path/to/file.py\n"
    "@@ -12,7 +12,7 @@ def example_function():\n"
    "-    old_code_line = 'This is the old code'\n"
    "+    new_code_line = 'This is the new code'\n"
    "     another_code_line = 'No change here'\n"
    "```\n"
    "Include only the necessary changes, and ensure they follow best practices for the language used.\n"
    "## Let's think step by step."
)

generate_git_diff_template = PromptTemplate(generate_git_diff_prompt_str)
