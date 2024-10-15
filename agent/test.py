from agent.constans.default import test_problem_statement, test_target_repository_name
from agent.constans.stage_3 import review_issue_to_locate_edit_position_template
from agent.llm import LLM
from agent.file_restorer import FileRestorer


async def start():
    restorer = FileRestorer("filtered_repo_structure.json")
    restored_content = restorer.restore_all_files()

    review_issue_to_locate_edit_position_message = (
        review_issue_to_locate_edit_position_template.format_messages(
            target_repository_name=test_target_repository_name,
            problem_statement=test_problem_statement,
            file_contents=restored_content,
        )
    )

    llm = LLM()
    response = await llm.chat(prompt=review_issue_to_locate_edit_position_message, n=4)
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(start())