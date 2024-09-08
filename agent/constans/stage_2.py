from llama_index.core import PromptTemplate

review_issue_with_file_structure_prompt_str = (
    "Please meticulously analyze the following GitHub problem description for the repository named {target_repository_name} which main languages is python and the associated file contents."
    "Based on the file structure provided, identify and select the functions or classes that you think need editing to resolve the issue.\n"
    "### GitHub Issue Description\n"
    "{github_issue_description}\n"
    "### Relevant files and their structure\n"
    "{relevant_files_structure}\n"
    "### Return the selected functions or classes in the following JSON format:\n"
    "{'files':[{'file_path':'path/to/file.py','classes':[{'class_name':'ClassName','methods':[{'method_name':'methodName'}]}],'variables':[{'variable_name':'variableName'}]}]}\n"
    "Details to Include:\n"
    "- File Path: The path of the file where the function or class is located.\n"
    "- Class Name: The name of the class that contains the method (if applicable).\n"
    "- Variable Name: The name of the variable that may need modification (if applicable).\n"
    "- Method Name: The name of the method (if applicable).\n"
)

review_issue_with_file_structure_template = PromptTemplate(
    review_issue_with_file_structure_prompt_str
)

test_review_issue_with_file_structure = """We are working on resolving a specific issue described in the GitHub issue for the repository named RepoAgent. We have identified relevant files and their structure to address this issue.

Task: Thoroughly review the GitHub issue description for the repository named RepoAgent. Based on the file structure provided, identify and select the functions or classes that you think need editing. Return the selected functions or classes in the following JSON format:

{
"path/to/file.py":
  "classes": [
    {
    "class_name": "ClassName",
    "functions": [
            {"function_name": "functionName"},
        ]
    },
  ]
}

Details to Include:

- File Path: The path of the file where the function or class is located.
- Class Name: The name of the class that contains the method (if applicable).
- Method Name: The name of the method (if applicable).

### GitHub Problem Description 

{'title': 'maximum recursion depth exceeded in comparison', 'body': 'Receiving the following error when : \r\n2024-07-09 12:48:43.996 | SUCCESS  | repo_agent.log:set_logger_level_from_config:74 - Log level set to INFO!\r\nparsing parent relationship:   0%|                                                                                      parsing parent relationship: 100%|█████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 8184.01it/s]\r\nLoading MetaInfo: /home/jovyan/work/Documentation/Arya/wiki/hierarchy_files\r\nMetaInfo is Refreshed and Saved\r\n2024-07-09 12:48:44.015 | INFO     | repo_agent.runner:first_generate:104 - Starting to generate documentation\r\nparsing bidirectional reference:   0%|                                                                                   | 0/2 [00:00<?, ?it/s]2024-07-09 12:48:44.198 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `column` parameter (6) is not in a valid range (0-0) for line 205 ('\\n').\r\n2024-07-09 12:48:44.198 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=Embed, file_path=wikiv1.py, line_number=205, column_number=6\r\n2024-07-09 12:48:44.208 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `line` parameter is not in a valid range.\r\n2024-07-09 12:48:44.208 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=create_collection, file_path=wikiv1.py, line_number=284, column_number=4\r\nparsing bidirectional reference:  50%|█████████████████████████████████████▌                                     | 1/2 [00:00<00:00,  5.17it/s]2024-07-09 12:48:44.212 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `column` parameter (6) is not in a valid range (0-0) for line 205 ('\\n').\r\n2024-07-09 12:48:44.213 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=Embed, file_path=.ipynb_checkpoints/wikiv1-checkpoint.py, line_number=205, column_number=6\r\n2024-07-09 12:48:44.220 | INFO     | repo_agent.doc_meta_info:find_all_referencer:293 - Error occurred: `line` parameter is not in a valid range.\r\n2024-07-09 12:48:44.220 | INFO     | repo_agent.doc_meta_info:find_all_referencer:294 - Parameters: variable_name=create_collection, file_path=.ipynb_checkpoints/wikiv1-checkpoint.py, line_number=284, column_number=4\r\nparsing bidirectional reference: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  9.74it/s]\r\nparsing topology task-list:   0%|                                                                                       | 0/10 [00:00<?, ?it/s]Traceback (most recent call last):\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/main.py", line 312, in <module>\r\n    cli()\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1157, in __call__\r\n    return self.main(*args, **kwargs)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1078, in main\r\n    rv = self.invoke(ctx)\r\n         ^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1688, in invoke\r\n    return _process_result(sub_ctx.command.invoke(sub_ctx))\r\n                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 1434, in invoke\r\n    return ctx.invoke(self.callback, **ctx.params)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/opt/conda/envs/repoenv/lib/python3.11/site-packages/click/core.py", line 783, in invoke\r\n    return __callback(*args, **kwargs)\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/main.py", line 260, in run\r\n    runner.run()\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/runner.py", line 240, in run\r\n    self.first_generate() # 如果是第一次做文档生成任务，就通过first_generate生成所有文档\r\n    ^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/runner.py", line 106, in first_generate\r\n    task_manager = self.meta_info.get_topology(\r\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/doc_meta_info.py", line 619, in get_topology\r\n    task_manager = self.get_task_manager(\r\n                   ^^^^^^^^^^^^^^^^^^^^^^\r\n  File "/home/jovyan/work/repoagent/RepoAgent/repo_agent/doc_meta_info.py", line 577, in get_task_manager\r\n    if task_available_func(child) and (child not in deal_items):\r\n                                       ^^^^^^^^^^^^^^^^^^^^^^^\r\n  File "<string>", line 4, in __eq__\r\n  File "<string>", line 4, in __eq__\r\n  File "<string>", line 4, in __eq__\r\n  [Previous line repeated 851 more times]\r\nRecursionError: maximum recursion depth exceeded in comparison\r\nparsing topology task-list:  90%|███████████████████████████████████████████████████████████████████████        | 9/10 [00:00<00:00, 34.28it/s]\r\n', 'author': 'Major-wagh'}

### Relevant files and their structure

./RepoAgent/repo_agent/doc_meta_info.py:
  Imports:
    import json
    import os
    import threading
    from dataclasses import dataclass, field
    from enum import Enum, auto, unique
    from pathlib import Path
    from typing import Any, Callable, Dict, List, Optional
    import jedi
    from colorama import Fore, Style
    from prettytable import PrettyTable
    from tqdm import tqdm
    from repo_agent.file_handler import FileHandler
    from repo_agent.log import logger
    from repo_agent.multi_task_dispatch import Task, TaskManager
    from repo_agent.settings import setting
    from repo_agent.utils.meta_info_utils import latest_verison_substring
  @unique
  class EdgeType:
    reference_edge = auto()
    subfile_edge = auto()
    file_item_edge = auto()
  @unique
  class DocItemType:
    _repo = auto()
    _dir = auto()
    _file = auto()
    _class = auto()
    _class_function = auto()
    _function = auto()
    _sub_function = auto()
    _global_var = auto()
    def to_str(self)
    def print_self(self)
    def get_edge_type(self, from_item_type: DocItemType, to_item_type: DocItemType)
  @unique
  class DocItemStatus:
    doc_up_to_date = auto()
    doc_has_not_been_generated = auto()
    code_changed = auto()
    add_new_referencer = auto()
    referencer_not_exist = auto()
  <top-level>:
    def need_to_generate(doc_item: DocItem) -> bool
  @dataclass
  class DocItem:
    item_type = DocItemType._class_function
    item_status = DocItemStatus.doc_has_not_been_generated
    obj_name = ""
    code_start_line = -1
    code_end_line = -1
    md_content = field(default_factory=list)
    content = field(default_factory=dict)
    children = field(default_factory=dict)
    father = None
    depth = 0
    tree_path = field(default_factory=list)
    max_reference_ansce = None
    reference_who = field(default_factory=list)
    who_reference_me = field(default_factory=list)
    special_reference_type = field(default_factory=list)
    reference_who_name_list = field(default_factory=list)
    who_reference_me_name_list = field(default_factory=list)
    has_task = False
    multithread_task_id = -1
    @staticmethod
    def has_ans_relation(now_a: DocItem, now_b: DocItem)
    def get_travel_list(self)
    def check_depth(self)
    def parse_tree_path(self, now_path)
    def get_file_name(self)
    def get_full_name(self)
    def find(self, recursive_file_path: list) -> Optional[DocItem]
    @staticmethod
    def check_has_task(now_item: DocItem)
    def print_recursive(self)

./RepoAgent/repo_agent/runner.py:
  Imports:
    import json
    import os
    import shutil
    import subprocess
    import threading
    import time
    from concurrent.futures import ThreadPoolExecutor
    from functools import partial
    from colorama import Fore, Style
    from tqdm import tqdm
    from repo_agent.change_detector import ChangeDetector
    from repo_agent.chat_engine import ChatEngine
    from repo_agent.doc_meta_info import DocItem, DocItemStatus, MetaInfo, need_to_generate
    from repo_agent.file_handler import FileHandler
    from repo_agent.log import logger
    from repo_agent.multi_task_dispatch import worker
    from repo_agent.project_manager import ProjectManager
    from repo_agent.settings import setting
    from repo_agent.utils.meta_info_utils import delete_fake_files, make_fake_files
  class Runner:
    def __init__(self)
    def get_all_pys(self, directory)
    def generate_doc_for_a_single_item(self, doc_item: DocItem)
    def first_generate(self)
    def markdown_refresh(self)
    def git_commit(self, commit_message)
    def run(self)
    def add_new_item(self, file_handler, json_data)
    def process_file_changes(self, repo_path, file_path, is_new_file)
    def update_existing_item(self, file_dict, file_handler, changes_in_pyfile)
    def update_object(self, file_dict, file_handler, obj_name, obj_referencer_list)
    def get_new_objects(self, file_handler)

./RepoAgent/repo_agent/utils/meta_info_utils.py:
  Imports:
    import itertools
    import os
    import git
    from colorama import Fore, Style
    from repo_agent.log import logger
    from repo_agent.settings import setting
  <top-level>:
    def make_fake_files()
    def delete_fake_files()

./RepoAgent/repo_agent/exceptions.py:
  Imports:
    from openai import APIConnectionError
    from repo_agent.log import logger
  class ErrorHandler:
    @staticmethod
    def handle_exception(e)
  class OpenAIError:
    def __init__(self, message)

./RepoAgent/repo_agent/settings.py:
  Imports:
    from enum import StrEnum
    from iso639 import Language, LanguageNotFoundError
    from pydantic import DirectoryPath, Field, HttpUrl, PositiveFloat, PositiveInt, SecretStr, field_serializer, field_validator
    from pydantic_settings import BaseSettings
    from repo_agent.config_manager import read_config, write_config
  class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
  class ProjectSettings:
    target_repo = ""
    hierarchy_name = ".project_doc_record"
    markdown_docs_name = "markdown_docs"
    ignore_list = []
    language = "Chinese"
    max_thread_count = 4
    max_document_tokens = 1024
    log_level = LogLevel.INFO
    @field_serializer("ignore_list")
    def serialize_ignore_list(self)
    @field_validator("language")
    @classmethod
    def validate_language_code(cls, v: str) -> str
    @field_validator("log_level", mode="before")
    @classmethod
    def set_log_level(cls, v: str) -> LogLevel
    @field_serializer("target_repo")
    def serialize_target_repo(self, target_repo: DirectoryPath)

"""

test_review_issue_with_file_structure_output = """
{ 
  "files": [
        {
          "file_path": "./RepoAgent/repo_agent/doc_meta_info.py",
          "classes": [
            { 
              "class_name": "DocItem",
              "methods": [ 
                { "method_name": "need_to_generate" },
                { "method_name": "has_ans_relation" },
                { "method_name": "get_travel_list" },
                { "method_name": "check_depth" },
                { "method_name": "parse_tree_path" },
                { "method_name": "get_file_name" },
                { "method_name": "get_full_name" },
                { "method_name": "find" },
                { "method_name": "check_has_task" },
                { "method_name": "print_recursive" }
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
                { "method_name": "get_all_pys" },
                { "method_name": "generate_doc_for_a_single_item" },
                { "method_name": "first_generate" },
                { "method_name": "markdown_refresh" },
                { "method_name": "git_commit" },
                { "method_name": "run" },
                { "method_name": "add_new_item" },
                { "method_name": "process_file_changes" },
                { "method_name": "update_existing_item" },
                { "method_name": "update_object" },
                { "method_name": "get_new_objects" }
              ]
            }
          ]
        }
      ] 
}
"""
