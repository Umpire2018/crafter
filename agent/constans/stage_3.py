from llama_index.core import PromptTemplate

review_issue_to_locate_edit_position_prompt_str = (
    "Please meticulously analyze the following GitHub problem description for the repository named {target_repository_name} which main languages is python and the associated file contents. Your task is to not only identify the specific locations within the codebase that require editing to address the issue but also to provide a reasoned justification for each suggested modification. "
    "Consider the broader context of the application and how these changes might affect its stability and performance.\n"
    "GitHub Problem Description:\n"
    "{problem_statement}\n"
    "Relevant File Contents:\n"
    "{file_contents}\n"
    "Instructions:\n"
    "- Identify the exact locations that need to be edited.\n"
    "- Explain why each identified location is critical to the resolution of the issue.\n"
    "- Provide your output in JSON format for clarity.\n"
    "Details to Include:\n"
    "- Line Numbers: The range of lines where the class, method, or function is located.\n"
    "Note: Precision in identifying the necessary edits is crucial as it directly influences the effectiveness and efficiency of the solution.\n"
)


review_issue_to_locate_edit_position_template = PromptTemplate(review_issue_to_locate_edit_position_prompt_str)

test_review_issue_to_locate_edit_position = """
"""