from llama_index.core import PromptTemplate

generate_code_modifications_prompt_str = (
    "Please analyze the following problem description and the identified source code snippet from the repository named {target_repository_name}, "
    "which primarily uses the {main_language} language. The snippet below has been identified as the relevant code to be modified. "
    "Based on the problem description, provide a detailed explanation of the necessary changes to the code using clear and accurate natural language. "
    "Describe the modifications step by step, specifying which parts of the code need to be changed and how. "
    "Ensure that your response is precise, avoids any inaccuracies or hallucinations, and follows best practices for the language used.\n\n"
    "## Relevant Algorithm to Solve the Problem:\n"
    "{retrieved_algorithm}\n\n"
    "### Problem Description:\n"
    "{problem_description}\n\n"
    "### Identified Source Code Snippet:\n"
    "{source_code}\n\n"
    "## Planning:\n"
    "{planning_of_problem}\n\n"
    "### Instructions for Code Modifications:\n"
    "Please provide the required changes below, including file paths, line numbers, and code snippets to assist in modifying the code.\n"
    "## Let's think step by step."
)


generate_code_modifications_template = PromptTemplate(
    generate_code_modifications_prompt_str
)

test_generate_git_diff_template_output = """
### Step 1: Identify the cause of the recursion error

The error message "maximum recursion depth exceeded in comparison" indicates that the Python interpreter has reached the maximum recursion depth, which is the limit on the number of recursive calls that can be made before a `RecursionError` is raised. This error typically occurs when there is either an infinite recursion loop or a very deep recursion that exceeds the default recursion depth limit.

### Step 2: Analyze the code where the recursion occurs

The recursion is occurring in the `check_depth` method of the `DocItem` class in the `doc_meta_info.py` file. This method is called recursively to calculate the depth of each node in the document hierarchy.

### Step 3: Determine if the recursion depth limit is exceeded

The error message suggests that the recursion depth limit is exceeded due to excessive recursive calls. This could be because the base case is not being reached or the recursive calls are not reducing the problem size sufficiently.

### Step 4: Refactor the code to reduce the number of recursive calls or correct the base case

To address the issue, we need to ensure that the base case is correctly defined and that the recursive calls are reducing the problem size. Here's how we can refactor the `check_depth` method:

```python
# 文件: ./RepoAgent/repo_agent/doc_meta_info.py
158:      def check_depth(self):
159:              '''
160:              Recursively calculates the depth of the node in the tree.
161:      
162:              Returns:
163:                  int: The depth of the node.
164:              '''
165:              if len(self.children) == 0:
166:                  self.depth = 0
167:                  return self.depth
168:              # Ensure that the recursive call is reducing the problem size
169:              max_child_depth = max(child.check_depth() for child in self.children)
170:              self.depth = max_child_depth + 1
171:              return self.depth
```

In this refactored code, we ensure that the base case is reached when there are no children, and we use a generator expression to calculate the maximum child depth, which should reduce the number of recursive calls.

### Step 5: Test the refactored code

After making the changes, we need to test the code to ensure that it no longer exceeds the recursion depth limit. This involves running the application with the modified code and observing if the `RecursionError` is resolved.

### Step 6: Optimize the code if necessary

If the code still performs sub-optimally, we can consider further optimizations, such as caching the results of the `check_depth` method to avoid recalculating the depth for nodes that have already been processed.

By following these steps, we should be able to resolve the `RecursionError` and improve the performance of the code.
"""
