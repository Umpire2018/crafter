from typing import List, Dict, Any

class EditResponseParser:
    def __init__(self, json_response: Dict[str, Any] | List[Dict[str, Any]]):
        self.data: Dict[str, Any] = {'files': []}

        # 如果输入是单个JSON对象，将其包装成列表以统一处理
        if isinstance(json_response, dict):
            json_response_list = [json_response]
        else:
            # 如果 json_response 是列表，直接使用它
            json_response_list = json_response

        files_list: List[Dict[str, Any]] = []

        # 处理每个JSON对象，提取其中的files字段
        for json_obj in json_response_list:
            files = json_obj.get('files', [])
            files_list.extend(files)

        self.data['files'] = files_list

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
        ,
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
