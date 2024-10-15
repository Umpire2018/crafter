from llama_index.core import PromptTemplate

# NOTE:
# 1. 可能出现文件不在目标仓库
# 2. 文件路径为以目标仓库开头，如 ./repo_agent/runners/__init__.py 而不是 ./RepoAgent/repo_agent/__init__.py
review_issue_with_file_structure_prompt_str = (
    "We are working on resolving a specific issue described in the GitHub issue for the repository named {target_repository_name} which main languages is {target_repository_language}. "
    "From the tree structure, select five files that you believe can assist in resolving the issue. \n"
    "### GitHub Issue Description\n"
    "{github_issue_description}\n"
    "### Repository Tree Structure\n"
    "{repository_tree_structure}\n"
    "Return the paths of these files, starting with the target repository's root, in the following JSON format:\n"
    "{{'possible_helping_files': ['./{target_repository_name}/file_name_template.py']}}"
)

review_issue_with_file_structure_template = PromptTemplate(
    review_issue_with_file_structure_prompt_str
)


test_review_issue_with_file_structure = """
Please thoroughly review the following GitHub issue description and the file structure of the associated GitHub repository names RepoAgent. From the file structure, select five files that you believe can assist in resolving the issue. Return the paths of these files, starting with the target repository's root, in the following JSON format:

{"possible_helping_files":["./RepoAgent/file1.py"]}

### GitHub Problem Description 

{'title': 'maximum recursion depth exceeded in comparison', 'body': 'Receiving the following error when : \r\n2024-07-09 12:48:43.996 | SUCCESS  | repo_agent.log:set_logger_level_from_config:74 - Log level set to INFO!\r\nparsing parent relationship:   0%|                                                                                      parsing parent relationship: 100%|█████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 8184.01it/s]\r\nLoading MetaInfo: /home/jovyan/work/Documentation/Arya/wiki/hierarchy_files\r\nMetaInfo is Refreshed and Saved\r\n2024-07-09 12:48:44.015 | INFO     | repo_agent.runner:first_generate:104 - Starting to generate documentation\r\nparsing bidirectional reference:   0%|                                                                                   | 0/2 [00:00<?, ?it/s]2024-07-09 12:48:44.198 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `column` parameter (6) is not in a valid range (0-0) for line 205 (\'\\n\').\r\n2024-07-09 12:48:44.198 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=Embed, file_path=wikiv1.py, line_number=205, column_number=6\r\n2024-07-09 12:48:44.208 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `line` parameter is not in a valid range.\r\n2024-07-09 12:48:44.208 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=create_collection, file_path=wikiv1.py, line_number=284, column_number=4\r\nparsing bidirectional reference:  50%|█████████████████████████████████████▌                                     | 1/2 [00:00<00:00,  5.17it/s]2024-07-09 12:48:44.212 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `column` parameter (6) is not in a valid range (0-0) for line 205 (\'\\n\').\r\n2024-07-09 12:48:44.213 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=Embed, file_path=.ipynb_checkpoints/wikiv1-checkpoint.py, line_number=205, column_number=6\r\n2024-07-09 12:48:44.220 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `line` parameter is not in a valid range.\r\n2024-07-09 12:48:44.220 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=create_collection, file_path=.ipynb_checkpoints/wikiv1-checkpoint.py, line_number=284, column_number=4\r\nparsing bidirectional reference: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  9.74it/s]\r\nparsing topology task-list:   0%|                                                                                       | 0/10 [00:00<?, ?it/s]Traceback (most recent call last):\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/main.py", line 312, in <module>\r\n    cli()\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1157, in __call__\r\n    return self.main(*args, **kwargs)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1078, in main\r\n    rv = self.invoke(ctx)\r\n         ^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1688, in invoke\r\n    return _process_result(sub_ctx.command.invoke(sub_ctx))\r\n                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1434, in invoke\r\n    return ctx.invoke(self.callback, **ctx.params)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 783, in invoke\r\n    return __callback(*args, **kwargs)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/main.py", line 260, in run\r\n    runner.run()\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/runner.py", line 240, in run\r\n    self.first_generate() # 如果是第一次做文档生成任务，就通过first_generate生成所有文档\r\n    ^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/runner.py", line 106, in first_generate\r\n    task_manager = self.meta_info.get_topology(\r\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/doc_meta_info.py", line 619, in get_topology\r\n    task_manager = self.get_task_manager(\r\n                   ^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/doc_meta_info.py", line 577, in get_task_manager\r\n    if task_available_func(child) and (child not in deal_items):\r\n                                       ^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "<string>", line 4, in __eq__\r\n  File "<string>", line 4, in __eq__\r\n  File "<string>", line 4, in __eq__\r\n  [Previous line repeated 851 more times]\r\nRecursionError: maximum recursion depth exceeded in comparison\r\nparsing topology task-list:  90%|███████████████████████████████████████████████████████████████████████        | 9/10 [00:00<00:00, 34.28it/s]\r\n', 'author': 'Major-wagh'}

### Repository Tree Structure 

RepoAgent
├── display
│   └── book_tools
│       ├── generate_repoagent_books.py
│       └── generate_summary_from_book.py
├── examples
│   └── init.py
├── repo_agent
│   ├── __init__.py
│   ├── __main__.py
│   ├── change_detector.py
│   ├── chat_engine.py
│   ├── chat_with_repo
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── gradio_interface.py
│   │   ├── json_handler.py
│   │   ├── main.py
│   │   ├── prompt.py
│   │   ├── rag.py
│   │   └── vectordb.py
│   ├── config_manager.py
│   ├── doc_meta_info.py
│   ├── exceptions.py
│   ├── file_handler.py
│   ├── log.py
│   ├── main.py
│   ├── multi_task_dispatch.py
│   ├── project_manager.py
│   ├── prompt.py
│   ├── runner.py
│   ├── settings.py
│   └── utils
│       ├── gitignore_checker.py
│       └── meta_info_utils.py
└── tests
    ├── __init__.py
    ├── test_change_detector.py
    ├── test_gradio_ui.py
    ├── test_json_handler.py
    ├── test_main.py
    ├── test_prompt.py
    ├── test_rag.py
    ├── test_structure_tree.py
    └── test_vectordb.py
"""

test_review_issue_with_file_structure_output = """
{
  "possible_helping_files": [
    "./RepoAgent/repo_agent/doc_meta_info.py",
    "./RepoAgent/repo_agent/runner.py",
    "./RepoAgent/repo_agent/utils/meta_info_utils.py",
    "./RepoAgent/repo_agent/exceptions.py",
    "./RepoAgent/repo_agent/settings.py"
  ]
}
"""
