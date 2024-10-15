from llama_index.core import PromptTemplate

self_retrieval_prompt_str = (
    "Given a problem, provide relevant problems then identify the algorithm behind it and also explain the tutorial of the algorithm.\n"
    "# Problem:\n"
    "{github_issue_description}\n"
    "# Exemplars:\n"
    "Recall {count_of_exemplars} relevant and distinct problems (different from the problem mentioned above). For each problem:\n"
    "1. describe it\n"
    "2. generate {target_repository_language} code step by step to solve that problem\n"
    "3. finally generate a plan to solve that problem\n"
    "# Algorithm:\n"
    "----------------\n"
    "Identify the algorithm (Brute-force, Dynamic Programming, Divide-and-conquer, Greedy, Backtracking, Recursive, Binary search, and so on) that needs to be used to solve the original problem.\n"
    "Write a useful tutorial about the above-mentioned algorithm. Provide a high-level generic tutorial for solving this type of problem. Do not generate code.\n"
    "Return the response in the following JSON format, considering the following guidelines:"
    "1. Do not use backticks (`) or backticks (```) or any markdown formatting in your response. All code should be included as plain text within the JSON fields."
    "2. Make sure that the JSON is syntactically correct and can be parsed directly without requiring further cleaning."
    "{\n"
    "    'problems': [\n"
    "        {\n"
    "            'description': 'Describe the problem.',\n"
    "            'code': 'Let\\'s think step by step to solve this problem in {target_repository_language} programming language.',\n"
    "            'planning': 'Plan to solve this problem.'\n"
    "        },\n"
    "        # Add more problems here...\n"
    "    ],\n"
    "    'algorithm': {\n"
    "        'tutorial': 'Write a useful tutorial about the identified algorithm.'\n"
    "    }\n"
    "}"
)

self_retrieval_prompt_template = PromptTemplate(
    self_retrieval_prompt_str
)

test_self_retrieval_prompt_output = """
{
    "problems": [
        {
            "description": "You are given a list of integers. Write a program to find the maximum sum of a contiguous subarray within a one-dimensional numeric array.",
            "code": [
                "def max_subarray_sum(arr):\\n",
                "    max_sum = arr[0]\\n",
                "    current_sum = arr[0]\\n",
                "    for i in range(1, len(arr)):\\n",
                "        current_sum = max(arr[i], current_sum + arr[i])\\n",
                "        max_sum = max(max_sum, current_sum)\\n",
                "    return max_sum\\n",
                "\\n",
                "# Example usage:\\n",
                "array = [-2, 1, -3, 4, -1, 2, 1, -5, 4]\\n",
                "print(max_subarray_sum(array))  # Output should be 6"
            ],
            "planning": "To solve this problem, we can use the Kadane's algorithm, which is an efficient way to find the maximum sum of a contiguous subarray. The algorithm works by iterating through the array and at each position, it decides whether to add the current element to the existing subarray or start a new subarray with the current element. The maximum sum encountered during the iteration is returned as the result."
        }
    ],
    "algorithm": {
        "tutorial": "Kadane's algorithm is a greedy algorithm used to find the maximum sum of a contiguous subarray within a one-dimensional numeric array. The algorithm works by iterating through the array and maintaining two variables: the current sum and the maximum sum found so far. At each position, the algorithm decides whether to add the current element to the existing subarray or start a new subarray with the current element. The decision is based on which option gives a higher sum. The algorithm has a time complexity of O(n), where n is the length of the array, making it an efficient solution for this problem."
    }
}
"""