review_issue_with_file_structure = """We are working on resolving a specific issue described in the GitHub issue for the repository named {target_repository_name}. We have identified relevant files and their structure to address this issue.

Task: Thoroughly review the GitHub issue description for the repository named {target_repository_name}. Based on the file structure provided, identify and select the functions or classes that you think need editing. Return the selected functions or classes in the following JSON format:

{
  "files": [
        {
        "file_path": "path/to/file.py",
        "classes": [
                {
                "class_name": "ClassName",
                "methods": [
                        {"method_name": "methodName"},
                    ]
                },
            ]
        }
    ]
}

Details to Include:

- File Path: The path of the file where the function or class is located.
- Class Name: The name of the class that contains the method (if applicable).
- Method Name: The name of the method (if applicable).

### GitHub Issue Description

{github_issue_description}

### Relevant files and their structure

{relevant_files_with_structure}
"""

test_review_issue_with_file_structure = """We are working on resolving a specific issue described in the GitHub issue for the repository named RepoAgent. We have identified relevant files and their structure to address this issue.

Task: Thoroughly review the GitHub issue description for the repository named RepoAgent. Based on the file structure provided, identify and select the functions or classes that you think need editing. Return the selected functions or classes in the following JSON format:

{
  "files": [
        {
        "file_path": "path/to/file.py",
        "classes": [
                {
                "class_name": "ClassName",
                "methods": [
                        {"method_name": "methodName"},
                    ]
                },
            ]
        }
    ]
}

Details to Include:

- File Path: The path of the file where the function or class is located.
- Class Name: The name of the class that contains the method (if applicable).
- Method Name: The name of the method (if applicable).

### GitHub Problem Description 

{'title': 'maximum recursion depth exceeded in comparison', 'body': 'Receiving the following error when : \r\n2024-07-09 12:48:43.996 | SUCCESS  | repo_agent.log:set_logger_level_from_config:74 - Log level set to INFO!\r\nparsing parent relationship:   0%|                                                                                      parsing parent relationship: 100%|█████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 8184.01it/s]\r\nLoading MetaInfo: /home/jovyan/work/Documentation/Arya/wiki/hierarchy_files\r\nMetaInfo is Refreshed and Saved\r\n2024-07-09 12:48:44.015 | INFO     | repo_agent.runner:first_generate:104 - Starting to generate documentation\r\nparsing bidirectional reference:   0%|                                                                                   | 0/2 [00:00<?, ?it/s]2024-07-09 12:48:44.198 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `column` parameter (6) is not in a valid range (0-0) for line 205 (\'\\n\').\r\n2024-07-09 12:48:44.198 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=Embed, file_path=wikiv1.py, line_number=205, column_number=6\r\n2024-07-09 12:48:44.208 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `line` parameter is not in a valid range.\r\n2024-07-09 12:48:44.208 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=create_collection, file_path=wikiv1.py, line_number=284, column_number=4\r\nparsing bidirectional reference:  50%|█████████████████████████████████████▌                                     | 1/2 [00:00<00:00,  5.17it/s]2024-07-09 12:48:44.212 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `column` parameter (6) is not in a valid range (0-0) for line 205 (\'\\n\').\r\n2024-07-09 12:48:44.213 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=Embed, file_path=.ipynb_checkpoints/wikiv1-checkpoint.py, line_number=205, column_number=6\r\n2024-07-09 12:48:44.220 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `line` parameter is not in a valid range.\r\n2024-07-09 12:48:44.220 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=create_collection, file_path=.ipynb_checkpoints/wikiv1-checkpoint.py, line_number=284, column_number=4\r\nparsing bidirectional reference: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  9.74it/s]\r\nparsing topology task-list:   0%|                                                                                       | 0/10 [00:00<?, ?it/s]Traceback (most recent call last):\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/main.py", line 312, in <module>\r\n    cli()\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1157, in __call__\r\n    return self.main(*args, **kwargs)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1078, in main\r\n    rv = self.invoke(ctx)\r\n         ^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1688, in invoke\r\n    return _process_result(sub_ctx.command.invoke(sub_ctx))\r\n                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1434, in invoke\r\n    return ctx.invoke(self.callback, **ctx.params)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 783, in invoke\r\n    return __callback(*args, **kwargs)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/main.py", line 260, in run\r\n    runner.run()\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/runner.py", line 240, in run\r\n    self.first_generate() # 如果是第一次做文档生成任务，就通过first_generate生成所有文档\r\n    ^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/runner.py", line 106, in first_generate\r\n    task_manager = self.meta_info.get_topology(\r\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/doc_meta_info.py", line 619, in get_topology\r\n    task_manager = self.get_task_manager(\r\n                   ^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/doc_meta_info.py", line 577, in get_task_manager\r\n    if task_available_func(child) and (child not in deal_items):\r\n                                       ^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "<string>", line 4, in __eq__\r\n  File "<string>", line 4, in __eq__\r\n  File "<string>", line 4, in __eq__\r\n  [Previous line repeated 851 more times]\r\nRecursionError: maximum recursion depth exceeded in comparison\r\nparsing topology task-list:  90%|███████████████████████████████████████████████████████████████████████        | 9/10 [00:00<00:00, 34.28it/s]\r\n', 'author': 'Major-wagh'}

### Relevant files and their structure

./RepoAgent/repo_agent/doc_meta_info.py:
  class DocItemType:
    def to_str(self)
    def print_self(self)
    def get_edge_type(self, from_item_type: DocItemType, to_item_type: DocItemType)
  class DocItemStatus:
    def need_to_generate(doc_item: DocItem) -> bool
  class DocItem:
    def has_ans_relation(now_a: DocItem, now_b: DocItem)
    def get_travel_list(self)
    def check_depth(self)
    def parse_tree_path(self, now_path)
    def get_file_name(self)
    def get_full_name(self)
    def find(self, recursive_file_path: list) -> Optional[DocItem]
    def check_has_task(now_item: DocItem)
    def print_recursive(self)
    def print_indent()
    def find_all_referencer(repo_path, variable_name, file_path, line_number, column_number)
  class MetaInfo:
    def init_meta_info(file_path_reflections, jump_files) -> MetaInfo
    def from_checkpoint_path(checkpoint_dir_path: str | Path) -> MetaInfo
    def checkpoint(self, target_dir_path: str | Path)
    def print_task_list(self, task_dict: Dict[Task])
    def get_all_files(self) -> List[DocItem]
    def walk_tree(now_node)
    def find_obj_with_lineno(self, file_node: DocItem, start_line_num) -> DocItem
    def parse_reference(self)
    def walk_file(now_obj: DocItem)
    def get_task_manager(self, now_node: DocItem, task_available_func) -> TaskManager
    def in_white_list(item: DocItem)
    def get_topology(self, task_available_func) -> TaskManager
    def _map(self, deal_func: Callable)
    def travel(now_item: DocItem)
    def load_doc_from_older_meta(self, older_meta: MetaInfo)
    def find_item(now_item: DocItem) -> Optional[DocItem]
    def travel(now_older_item: DocItem)
    def travel2(now_older_item: DocItem)
    def from_project_hierarchy_path(repo_path: str) -> MetaInfo
    def to_hierarchy_json(self)
    def walk_file(now_obj: DocItem)
    def from_project_hierarchy_json(project_hierarchy_json) -> MetaInfo
    def code_contain(item, other_item) -> bool
    def change_items(now_item: DocItem)
./RepoAgent/repo_agent/runner.py:
  class Runner:
    def __init__(self)
    def get_all_pys(self, directory)
    def generate_doc_for_a_single_item(self, doc_item: DocItem)
    def first_generate(self)
    def markdown_refresh(self)
    def recursive_check(doc_item: DocItem) -> bool
    def to_markdown(item: DocItem, now_level: int) -> str
    def git_commit(self, commit_message)
    def run(self)
    def add_new_item(self, file_handler, json_data)
    def process_file_changes(self, repo_path, file_path, is_new_file)
    def update_existing_item(self, file_dict, file_handler, changes_in_pyfile)
    def update_object(self, file_dict, file_handler, obj_name, obj_referencer_list)
    def get_new_objects(self, file_handler)
./RepoAgent/repo_agent/utils/meta_info_utils.py:
  class Runner:
    def make_fake_files()
    def delete_fake_files()
    def gci(filepath)
./RepoAgent/repo_agent/exceptions.py:
  class ErrorHandler:
    def handle_exception(e)
  class OpenAIError:
    def __init__(self, message)
./RepoAgent/repo_agent/settings.py:
  class ProjectSettings:
    def serialize_ignore_list(self)
    def validate_language_code(cls, v: str) -> str
    def set_log_level(cls, v: str) -> LogLevel
    def serialize_target_repo(self, target_repo: DirectoryPath)
  class ChatCompletionSettings:
    def serialize_base_url(self, base_url: HttpUrl)

"""

test_review_issue_with_file_structure_output = """
{
  "files": [
        {
            "file_path": "./RepoAgent/repo_agent/doc_meta_info.py",
            "classes": [
                {
                    "class_name": "DocItemStatus",
                    "methods": [
                        {"method_name": "need_to_generate"}
                    ]
                },
                {
                    "class_name": "DocItem",
                    "methods": [
                        {"method_name": "has_ans_relation"},
                        {"method_name": "get_travel_list"},
                        {"method_name": "check_depth"},
                        {"method_name": "parse_tree_path"},
                        {"method_name": "get_file_name"},
                        {"method_name": "get_full_name"},
                        {"method_name": "find"},
                        {"method_name": "check_has_task"},
                        {"method_name": "print_recursive"}
                    ]
                },
                {
                    "class_name": "MetaInfo",
                    "methods": [
                        {"method_name": "get_topology"},
                        {"method_name": "in_white_list"},
                        {"method_name": "travel"}
                    ]
                }
            ]
        },
        {
            "file_path": "./RepoAgent/repo_agent/runner.py",
            "classes": [
                {
                    "class_name": "Runner",
                    "methods": [
                        {"method_name": "first_generate"}
                    ]
                }
            ]
        }
    ]
}
"""
