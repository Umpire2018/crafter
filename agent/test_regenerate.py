from agent.file_restorer import FileRestorer
from agent.constans.stage_3 import test_review_issue_to_locate_edit_position_output
from agent.constans.regenerate_git_diff import regenerate_git_diff_template
from agent.constans.generate import test_generate_git_diff_template_output
from agent.llm import LLM


async def start():
    restorer = FileRestorer("filtered_repo_structure.json")
    restored_content = restorer.restore_files_from_issues(
        test_review_issue_to_locate_edit_position_output
    )

    llm = LLM()

    regenerate_git_diff_message = regenerate_git_diff_template.format_messages(
        source_code=restored_content,
        modification_instructions=test_generate_git_diff_template_output,
    )
    regenerate_response = await llm.chat(prompt=regenerate_git_diff_message)
    print(regenerate_response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(start())
