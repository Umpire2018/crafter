from llama_index.core import PromptTemplate

self_retrieval_prompt_str = (
    "Given a problem, provide relevant problems, then identify the algorithm behind it and explain the tutorial of the algorithm.\n"
    "# Problem:\n"
    "{github_issue_description}\n"
    "# Exemplars:\n"
    "Recall {count_of_exemplars} relevant and distinct problems (different from the problem mentioned above). For each problem:\n"
    "1. Describe the problem.\n"
    "2. Generate {target_repository_language} code step by step to solve that problem.\n"
    "   - Make sure the code is provided as a list of strings, where each line of code is a separate string in the list.\n"
    "3. Finally, generate a plan to solve that problem.\n"
    "# Algorithm:\n"
    "----------------\n"
    "Identify the algorithm (e.g., Brute-force, Dynamic Programming, Divide-and-conquer, Greedy, Backtracking, Recursive, Binary search, etc.) that needs to be used to solve the original problem.\n"
    "Write a useful tutorial about the above-mentioned algorithm. Provide a high-level, generic tutorial for solving this type of problem. Do not generate code.\n"
    "Return the response in the following JSON format, considering the following guidelines:\n"
    "1. Do not use backticks (`), triple backticks (```), or any markdown formatting in your response. All code should be included as plain text within the JSON fields.\n"
    "2. Make sure the code is provided as a list of strings, where each line of code is a separate string in the list.\n"
    "{\n"
    '    "problems": [\n'
    "        {\n"
    '            "description": "Describe the problem.",\n'
    '            "code": [\n'
    '                "Let’s think step by step to solve this problem in {target_repository_language} programming language."\n'
    "            ],\n"
    '            "planning": "Plan to solve this problem."\n'
    "        }\n"
    "    ],\n"
    '    "algorithm": {\n'
    '        "tutorial": "Write a useful tutorial about the identified algorithm."\n'
    "    }\n"
    "}"
)


self_retrieval_prompt_template = PromptTemplate(self_retrieval_prompt_str)

test_self_retrieval_prompt_output = """
{
    "problems": [
        {
            "description": "You are given a list of numbers. Write a program to find the maximum sum of a contiguous subarray within a one-dimensional numeric array.",
            "code": "def max_subarray_sum(arr):\\n\\n    max_so_far = arr[0]\\n\\n    max_ending_here = arr[0]\\n\\n    for i in range(1, len(arr)):\\n\\n        max_ending_here = max(arr[i], max_ending_here + arr[i])\\n\\n        max_so_far = max(max_so_far, max_ending_here)\\n\\n    return max_so_far\\n\\narr = [1, -3, 2, 1, -1]\\n\\nprint(max_subarray_sum(arr))",
            "planning": "To solve this problem, we can use Kadane's algorithm, which is an efficient way to find the maximum sum of a contiguous subarray. The algorithm works by iterating through the array and at each position, it decides whether to add the current element to the existing subarray or start a new subarray with the current element. The maximum sum encountered so far is kept updated throughout the iteration."
        },
        {
            "description": "You are given a string. Write a program to check if the string is a palindrome. A palindrome is a string that reads the same backward as forward.",
            "code": "def is_palindrome(s):\\n\\n    return s == s[::-1]\\n\\ns = 'racecar'\\n\\nprint(is_palindrome(s))",
            "planning": "To check if a string is a palindrome, we can compare the string with its reverse. If they are the same, then the string is a palindrome. This can be done by using Python's slicing feature to reverse the string and then comparing it with the original string."
        }
    ],
    "algorithm": {
        "tutorial": "The algorithm used to solve the original problem is a recursive algorithm. Recursive algorithms are those that solve a problem by breaking it down into smaller, similar subproblems. The key characteristics of a recursive algorithm are:\\n\\n1. Base Case: A condition that stops the recursion. Without a base case, the recursion would continue indefinitely.\\n2. Recursive Case: A condition that breaks the problem down into smaller subproblems.\\n3. Recursive Call: The function calls itself with a modified set of parameters.\\n\\nTo solve a problem using recursion, you need to identify the base case and the recursive case. The base case provides the stopping condition, and the recursive case breaks the problem down into smaller subproblems. By solving the smaller subproblems, you can build up to the solution of the original problem."
    }
}
"""
