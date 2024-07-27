import tree_sitter
from tree_sitter import Language, Parser


class CodeEditor:
    def __init__(self, source_code: str, language: str):
        self.source_code = source_code
        self.language = language
        self.parser = Parser()
        self.parser.set_language(Language(language))
        self.tree = self.parser.parse(source_code.encode("utf-8"))

    def parse(self):
        self.tree = self.parser.parse(self.source_code.encode("utf-8"))

    def find_node_by_type(self, node_type: str) -> list[tree_sitter.Node]:
        cursor = self.tree.walk()
        nodes = []

        while True:
            if cursor.node.type == node_type:
                nodes.append(cursor.node)
            if cursor.goto_first_child():
                continue
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    return nodes

    def insert_code(self, position: int, code: str):
        self.source_code = (
            self.source_code[:position] + code + self.source_code[position:]
        )
        self.parse()

    def delete_code(self, start_position: int, end_position: int):
        self.source_code = (
            self.source_code[:start_position] + self.source_code[end_position:]
        )
        self.parse()

    def replace_code(self, start_position: int, end_position: int, code: str):
        self.source_code = (
            self.source_code[:start_position] + code + self.source_code[end_position:]
        )
        self.parse()

    def get_function_signature(
        self, function_name: str
    ) -> tuple[list[tuple[str, str]], str]:
        nodes = self.find_node_by_type("function_definition")
        for node in nodes:
            name_node = node.child_by_field_name("name")
            if name_node and name_node.text.decode("utf-8") == function_name:
                return self._get_function_signature(node)
        return [], ""

    def _get_function_signature(
        self, node: tree_sitter.Node
    ) -> tuple[list[tuple[str, str]], str]:
        parameters = []
        return_type = None
        param_node = node.child_by_field_name("parameters")
        if param_node:
            for param in param_node.children:
                param_name = None
                param_type = "Any"
                if param.type == "typed_parameter":
                    for child in param.children:
                        if child.type == "identifier":
                            param_name = child.text.decode("utf-8")
                        elif child.type == "type":
                            param_type = child.text.decode("utf-8")
                else:
                    param_name = param.text.decode("utf-8")
                if param_name:
                    parameters.append((param_name, param_type))
        return_type_node = node.child_by_field_name("return_type")
        if return_type_node:
            return_type = return_type_node.text.decode("utf-8")
        return parameters, return_type

    def get_class_definition(self, class_name: str) -> tree_sitter.Node:
        nodes = self.find_node_by_type("class_definition")
        for node in nodes:
            name_node = node.child_by_field_name("name")
            if name_node and name_node.text.decode("utf-8") == class_name:
                return node
        return None

    def save(self, file_path: str):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.source_code)


if __name__ == "__main__":
    source_code = """
class Example:
    def sync_function(self):
        pass

    async def async_function(self):
        pass
"""
    editor = CodeEditor(source_code, "tree_sitter_python")

    # 查找函数定义
    functions = editor.find_node_by_type("function_definition")
    for func in functions:
        print(
            f'Function name: {editor.get_node_text(func.child_by_field_name("name"), source_code)}'
        )

    # 插入代码
    editor.insert_code(0, "# This is a new line\n")
    print(editor.source_code)

    # 删除代码
    editor.delete_code(0, 20)
    print(editor.source_code)

    # 替换代码
    editor.replace_code(0, 20, "# Replaced line\n")
    print(editor.source_code)

    # 获取函数签名
    parameters, return_type = editor.get_function_signature("async_function")
    print(f"Parameters: {parameters}, Return type: {return_type}")

    # 保存修改后的代码
    editor.save("edited_example.py")
