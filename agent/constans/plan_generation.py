from llama_index.core import PromptTemplate

plan_generation_prompt_str = (
    "Given a competitive programming problem generate a concrete planning to solve the problem.\n"
    "# Problem: {problem_description}\n"
    "# Planning: {planning_of_exemplar}\n"
    "## Relevant Algorithm to solve the next problem: {retrieved_algorithm}\n"
    "## Problem to be solved: {original_problem}\n"
    "## Planning:\n"
    "----------------\n"
    "Important: You should give only the planning to solve the problem. Do not add extra explanation or words."
)

plan_generation_prompt_template = PromptTemplate(plan_generation_prompt_str)

test_plan_generation_prompt_output = """
1. Identify the cause of the recursion error.
2. Analyze the code where the recursion occurs.
3. Determine if the recursion depth limit is exceeded due to excessive recursive calls or incorrect base case.
4. Refactor the code to reduce the number of recursive calls or correct the base case.
5. Test the refactored code to ensure it no longer exceeds the recursion depth limit.
6. Optimize the code if necessary for better performance.
"""

confidence_generation_prompt_str = (
    "Given a competitive programming problem and a plan to solve the problem in {target_repository_language}, tell whether the plan is correct to solve this problem.\n"
    "# Problem: {original_problem}\n"
    "# Planning:\n"
    "{planning_of_original_problem}\n"
    "----------------\n"
    "Important: Your response must follow the following json format:\n"
    "{\n"
    '"explanation": "Discuss whether the given competitive programming problem is solvable by using the above mentioned planning.",\n'
    '"confidence": "Confidence score regarding the solvability of the problem. Must be an integer between 0 and 100."\n'
    "}"
)

confidence_generation_template = PromptTemplate(confidence_generation_prompt_str)

test_confidence_generation_output = """{
"explanation": "The given problem description is not a competitive programming problem but rather a debugging scenario from a Python application. The plan provided is a systematic approach to resolving a specific type of error (RecursionError: maximum recursion depth exceeded in comparison) in the context of this application. The plan is correct for solving this particular issue within the application, as it follows a logical sequence of steps to identify and fix the cause of the recursion error. The steps involve identifying the cause, analyzing the code, refactoring, testing, and optimizing. These steps are generally applicable to debugging recursive functions in Python and are appropriate for the given scenario.",
"confidence": 95
}
"""
