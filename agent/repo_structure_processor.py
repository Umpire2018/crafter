# agent/repo_structure_processor.py
import json
from typing import Optional, Dict, List
from agent.schemas import (
    FileMapType,
    FileData,
    ClassInfo,
    FunctionInfo,
    SimpleFileData,
    SimpleFileMapType,
    SimpleFunctionInfo,
)
from pydantic import FilePath


# 使用你定义的 Pydantic 模型
class RepoStructureProcessor:
    def __init__(self, repo_structure_path: FilePath):
        """
        初始化时，加载并解析 repo_structure.json 文件，生成 Pydantic 模型。
        """
        # 加载 repo_structure.json 文件
        with open(repo_structure_path, "r") as f:
            repo_structure_dict = json.load(f)

        # 手动解析字典中的每个值为 Pydantic 模型
        self.repo_structure: FileMapType = {
            file_path: FileData.model_validate(file_data)
            for file_path, file_data in repo_structure_dict.items()
        }

    def extract_class_methods(self, input_json_data: SimpleFileMapType):
        """
        提取与输入 JSON 匹配的类和方法，并返回经过处理的 JSON 数据。
        """
        results: FileMapType = {}

        input_json_data: SimpleFileMapType = {
            file_path: SimpleFileData.model_validate(data)
            for file_path, data in input_json_data.items()
        }

        for input_file_path, input_class_item in input_json_data.items():
            repo_file_data = self.repo_structure.get(input_file_path)

            if repo_file_data:
                results[input_file_path] = FileData(
                    imports=repo_file_data.imports,
                    top_level=repo_file_data.top_level,
                    classes=[],
                )

                for input_class in input_class_item.classes:
                    input_class_name = input_class.class_name
                    input_methods = input_class.functions

                    # 获取 repo_structure.json 中匹配的类信息
                    repo_class_data = self.find_class_in_repo(
                        input_class_name, repo_file_data.classes
                    )

                    if repo_class_data:
                        # 只保留匹配的函数，删除不匹配的函数
                        matched_functions = self.filter_functions(
                            input_methods, repo_class_data.functions
                        )
                        if matched_functions:
                            # 将匹配到的类和方法加入结果
                            modified_class_info = ClassInfo(
                                class_name=repo_class_data.class_name,
                                class_decorators=repo_class_data.class_decorators,
                                expressions=repo_class_data.expressions,
                                functions=matched_functions,
                                start_line=repo_class_data.start_line,
                                end_line=repo_class_data.end_line,
                            )
                            results[input_file_path].classes.append(modified_class_info)

        return results

    def find_class_in_repo(
        self, class_name: str, class_info: List[ClassInfo]
    ) -> Optional[ClassInfo]:
        """
        在 repo_structure.json 中查找匹配的类信息。
        """
        for class_data in class_info:
            if class_data.class_name == class_name:
                return class_data
        return None

    def filter_functions(
        self,
        input_methods: List[SimpleFunctionInfo],
        class_functions: List[FunctionInfo],
    ) -> List[FunctionInfo]:
        """
        过滤函数，只保留在输入中匹配的函数。
        """
        matched_functions = []

        for input_method in input_methods:
            input_method_name = input_method.function_name
            for repo_method in class_functions:
                if repo_method.function_name == input_method_name:
                    matched_functions.append(repo_method)

        return matched_functions


# 初始化处理器时加载 repo_structure.json
processor = RepoStructureProcessor(repo_structure_path="./repo_structure.json")

input_json_data = {
    "./RepoAgent/repo_agent/doc_meta_info.py": {
        "classes": [
            {
                "class_name": "DocItem",
                "functions": [
                    {"function_name": "check_depth"},
                    {"function_name": "parse_tree_path"},
                    {"function_name": "get_file_name"},
                    {"function_name": "get_full_name"},
                    {"function_name": "find"},
                    {"function_name": "print_recursive"},
                ],
            },
            {
                "class_name": "MetaInfo",
                "functions": [{"function_name": "get_topology"}],
            },
        ]
    },
    "./RepoAgent/repo_agent/runner.py": {
        "classes": [
            {
                "class_name": "Runner",
                "functions": [
                    {"function_name": "first_generate"},
                    {"function_name": "run"},
                ],
            }
        ]
    },
}

if __name__ == "__main__":
    # 提取相关的类方法文本信息并返回符合条件的 JSON 块
    result = processor.extract_class_methods(input_json_data)

    # 序列化所有数据并写入 JSON 文件
    json_content = json.dumps(
        {k: v.model_dump() for k, v in result.items()},
        ensure_ascii=False,
        indent=2,
    )

    with open("filtered_repo_structure.json", "w", encoding="utf-8") as f:
        f.write(json_content)
