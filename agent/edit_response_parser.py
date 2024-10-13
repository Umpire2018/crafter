import json
from typing import List, Dict, Any

class EditResponseParser:
    def __init__(self, json_response: str | List[str]):
        self.data: Dict[str, Any] = {'files': []}

        if isinstance(json_response, str):
            json_str_list = [json_response]
        else:
            # If json_response is a list of strings, process each one separately
            json_str_list = json_response

        files_list: List[Dict[str, Any]] = []

        for json_str in json_str_list:
            try:
                data = self.parse_json_string(json_str)
                files = data.get('files', [])
                files_list.extend(files)
            except json.decoder.JSONDecodeError as e:
                print(f"Failed to parse JSON string: {e}")

        self.data['files'] = files_list

    def parse_json_string(self, json_str: str) -> Dict[str, Any]:
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-len("```")].strip()
        return json.loads(json_str)

    def get_files(self) -> List[Dict[str, Any]]:
        """Return the entire list of files with their edits, maintaining the hierarchy."""
        return self.data.get('files', [])

    def get_file_names(self) -> List[str]:
        """Extract and return all file names from the response."""
        return [file['file_name'] for file in self.data.get('files', [])]

    def get_edits_for_file(self, file_name: str) -> List[Dict[str, Any]]:
        """Retrieve the edits for a specific file."""
        for file in self.data.get('files', []):
            if file['file_name'] == file_name:
                return file.get('edits', [])
        return []

    def get_all_edits(self) -> List[Dict[str, Any]]:
        """Return all edits across all files, maintaining the original JSON structure."""
        return self.data.get('files', [])

# Example usage
if __name__ == "__main__":
    json_response_list = [
        '''```json
        {
          "files": [
            {
              "file_name": "./RepoAgent/repo_agent/doc_meta_info.py",
              "edits": [
                {
                  "reason": "The recursive function `check_depth` is causing a maximum recursion depth exceeded error.",
                  "line_numbers": {
                    "start": 158,
                    "end": 173
                  }
                }
              ]
            }
          ]
        }
        ```''',
        '''```json
        {
          "files": [
            {
              "file_name": "./RepoAgent/repo_agent/runner.py",
              "edits": [
                {
                  "reason": "The `first_generate` method is calling `get_topology`, leading to recursion.",
                  "line_numbers": {
                    "start": 105,
                    "end": 108
                  }
                }
              ]
            }
          ]
        }
        ```''', '```json\n{\n  "files": [\n    {\n      "file_name": "./RepoAgent/repo_agent/doc_meta_info.py",\n      "edits": [\n        {\n          "reason": "The recursive __eq__ calls are causing the maximum recursion depth to be exceeded. This is likely due to circular references or incorrect comparison logic.",\n          "line_numbers": {\n            "start": 577,\n            "end": 577\n          }\n        },\n        {\n          "reason": "The recursive __eq__ calls are causing the maximum recursion depth to be exceeded. This is likely due to circular references or incorrect comparison logic.",\n          "line_numbers": {\n            "start": 578,\n            "end": 578\n          }\n        },\n        {\n          "reason": "The recursive __eq__ calls are causing the maximum recursion depth to be exceeded. This is likely due to circular references or incorrect comparison logic.",\n          "line_numbers": {\n            "start": 579,\n            "end": 579\n          }\n        }\n      ]\n    },\n    {\n      "file_name": "./RepoAgent/repo_agent/main.py",\n      "edits": [\n        {\n          "reason": "The recursive calls to the functions that involve the DocItem class are causing the maximum recursion depth to be exceeded. This needs to be addressed by refactoring the code to avoid deep recursion.",\n          "line_numbers": {\n            "start": 312,\n            "end": 312\n          }\n        }\n      ]\n    }\n  ]\n}\n```', '```json\n{\n  "files": [\n    {\n      "file_name": "./RepoAgent/repo_agent/doc_meta_info.py",\n      "edits": [\n        {\n          "reason": "The recursive method \'check_depth\' is likely causing the maximum recursion depth to be exceeded due to the large number of iterations. This is a common issue in tree-like structures where each node has multiple children.",\n          "line_numbers": {\n            "start": 158,\n            "end": 173\n          }\n        },\n        {\n          "reason": "The method \'get_full_name\' appears to be causing multiple calls to itself recursively, which can also lead to a maximum recursion depth exceeded error.",\n          "line_numbers": {\n            "start": 199,\n            "end": 214\n          }\n        },\n        {\n          "reason": "The method \'find\' may also be contributing to the recursion issue, especially if the recursive_file_path is very long.",\n          "line_numbers": {\n            "start": 228,\n            "end": 236\n          }\n        },\n        {\n          "reason": "The method \'print_recursive\' may be calling itself recursively if the print_content flag is set to True and there are many child items to print.",\n          "line_numbers": {\n            "start": 246,\n            "end": 267\n          }\n        }\n      ]\n    },\n    {\n      "file_name": "./RepoAgent/repo_agent/runner.py",\n      "edits": [\n        {\n          "reason": "The method \'first_generate\' may be recursively calling itself or other methods that cause recursion if the document generation process is interrupted or there are many files to process.",\n          "line_numbers": {\n            "start": 104,\n            "end": 144\n          }\n        },\n        {\n          "reason": "The method \'run\' may be causing recursion in the \'get_topology\' method if there are many files or changes to process.",\n          "line_numbers": {\n            "start": 232,\n            "end": 300\n          }\n        }\n      ]\n    }\n  ]\n}\n```'
    ]

    parser = EditResponseParser(json_response_list)

    # Get all file entries (maintaining hierarchical structure)
    files = parser.get_files()
    print("Files and their edits:")
    for file in files:
        print(f"File: {file['file_name']}")
        for edit in file.get('edits', []):
            print(f"  Reason: {edit['reason']}")
            print(f"  Line Numbers: {edit['line_numbers']}")
        print()

    # Get all file names
    file_names = parser.get_file_names()
    print("File Names:")
    for name in file_names:
        print(name)

    # Get edits for a specific file
    edits = parser.get_edits_for_file("./RepoAgent/repo_agent/doc_meta_info.py")
    print("\nEdits for './RepoAgent/repo_agent/doc_meta_info.py':")
    for edit in edits:
        print(f"Reason: {edit['reason']}")
        print(f"Line Numbers: {edit['line_numbers']}")
