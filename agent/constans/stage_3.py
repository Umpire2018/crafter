from llama_index.core import PromptTemplate

review_issue_to_locate_edit_position_prompt_str = (
    "Please meticulously analyze the following GitHub problem description for the repository named {target_repository_name} which main languages is python and the associated file contents. Your task is to not only identify the specific locations within the codebase that require editing to address the issue but also to provide a reasoned justification for each suggested modification. "
    "Consider the broader context of the application and how these changes might affect its stability and performance.\n"
    "### GitHub Problem Description:\n"
    "{problem_statement}\n"
    "Relevant File Contents:\n"
    "{file_contents}\n"
    "### Instructions:\n"
    "- Identify the exact locations that need to be edited.\n"
    "- Explain why each identified location is critical to the resolution of the issue.\n"
    "- Provide your output in JSON format for clarity.\n"
    "- Make sure your response is wrapped in triple backticks ```json and ends with ``` without additional content outside this block.\n"
    "### Desired JSON Output Format:\n"
    "{{\n"
    "  \"files\": [\n"
    "    {{\n"
    "      \"file_name\": \"relative/path/to/file.py\",\n"
    "      \"edits\": [\n"
    "        {{\n"
    "          \"reason\": \"Brief explanation of why this part of the code needs to be modified.\",\n"
    "          \"line_numbers\": {{\n"
    "            \"start\": line_number_start,\n"
    "            \"end\": line_number_end\n"
    "          }}\n"
    "        }}\n"
    "      ]\n"
    "    }}\n"
    "  ]\n"
    "}}\n"
    "### Note:\n"
    "Precision in identifying the necessary edits is crucial as it directly influences the effectiveness and efficiency of the solution.\n"
)


review_issue_to_locate_edit_position_template = PromptTemplate(
    review_issue_to_locate_edit_position_prompt_str
)

test_review_issue_to_locate_edit_position_output = """
```json
{
  "files": [
    {
      "file_name": "./RepoAgent/repo_agent/doc_meta_info.py",
      "edits": [
        {
          "reason": "The recursive function `check_depth` is causing a maximum recursion depth exceeded error due to infinite recursion. This is likely caused by the `__eq__` method being called recursively without a base case.",
          "line_numbers": {
            "start": 158,
            "end": 173
          }
        },
        {
          "reason": "The `__eq__` method is being called recursively without a base case, which is causing the maximum recursion depth exceeded error. This method should include a base case to prevent infinite recursion.",
          "line_numbers": {
            "start": 4,
            "end": 4
          }
        }
      ]
    },
    {
      "file_name": "./RepoAgent/repo_agent/runner.py",
      "edits": [
        {
          "reason": "The `first_generate` method is calling `get_topology` which in turn calls `get_task_manager` which uses the `__eq__` method of `DocItem`. This method should be modified to prevent infinite recursion.",
          "line_numbers": {
            "start": 105,
            "end": 108
          }
        },
        {
          "reason": "The `run` method is calling `get_task_manager` which uses the `__eq__` method of `DocItem`. This method should be modified to prevent infinite recursion.",
          "line_numbers": {
            "start": 269,
            "end": 272
          }
        }
      ]
    }
  ]
}
```
"""