# agent/repo_structure_processor.py
import json
from agent.schemas import (
    FileMapType,
    FileData,
    SimpleFileData,
    SimpleFileMapType,
)
from pydantic import FilePath
from agent.structure_filter import StructureFilter


class RepoStructureProcessor:
    def __init__(self, repo_structure_path: FilePath):
        """
        初始化时，加载并解析 repo_structure.json 文件，生成 Pydantic 模型。
        """
        with open(repo_structure_path, "r") as f:
            repo_structure_dict = json.load(f)

        self.repo_structure: FileMapType = {
            file_path: FileData.model_validate(file_data)
            for file_path, file_data in repo_structure_dict.items()
        }

        self.filter = StructureFilter(self.repo_structure)

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
                # 筛选类
                class_names = [cls.class_name for cls in input_class_item.classes]
                filtered_file_data = self.filter.filter_classes(
                    repo_file_data, class_names
                )

                # 对每个类进行函数筛选
                for cls in filtered_file_data.classes:
                    input_class = next(
                        (
                            c
                            for c in input_class_item.classes
                            if c.class_name == cls.class_name
                        ),
                        None,
                    )
                    if input_class:
                        function_names = [
                            func.function_name for func in input_class.functions
                        ]
                        filtered_class = self.filter.filter_functions(
                            cls, function_names
                        )
                        cls.functions = filtered_class.functions
                results[input_file_path] = filtered_file_data

        return results

    def save_filtered_structure(
        self, filtered_structure: FileMapType, output_path: str
    ):
        """
        将过滤后的结构保存为 JSON 文件。
        """
        json_content = json.dumps(
            {k: v.model_dump() for k, v in filtered_structure.items()},
            ensure_ascii=False,
            indent=2,
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_content)


if __name__ == "__main__":
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

    filtered_structure = processor.extract_class_methods(input_json_data)
    processor.save_filtered_structure(
        filtered_structure, "filtered_repo_structure.json"
    )
