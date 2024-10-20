from agent.file_restorer import FileRestorer
from agent.constans.stage_3 import test_review_issue_to_locate_edit_position_output


async def start():
    restorer = FileRestorer("filtered_repo_structure.json")
    restored_content = restorer.restore_files_from_issues(
        test_review_issue_to_locate_edit_position_output
    )

    print(restored_content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(start())
