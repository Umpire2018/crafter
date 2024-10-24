from agent.file_restorer import FileRestorer
from agent.constans.stage_3 import test_review_issue_to_locate_edit_position_output
from agent.constans.default import (
    test_problem_statement,
    test_target_repository_name,
    test_target_repository_language,
)
from agent.constans.generate import (
    generate_code_modifications_template,
)
from agent.constans.self_retrieval import test_self_retrieval_prompt_output
from agent.constans.problem_set_model import ProblemSet
from agent.constans.plan_generation import test_plan_generation_prompt_output
from agent.llm import LLM


async def start():
    restorer = FileRestorer("filtered_repo_structure.json")
    restored_content = restorer.restore_files_from_issues(
        test_review_issue_to_locate_edit_position_output
    )

    problem_set = ProblemSet.model_validate_json(test_self_retrieval_prompt_output)

    generate_code_modifications_message = (
        generate_code_modifications_template.format_messages(
            target_repository_name=test_target_repository_name,
            main_language=test_target_repository_language,
            retrieved_algorithm=problem_set.algorithm,
            planning_of_problem=test_plan_generation_prompt_output,
            problem_description=test_problem_statement,
            source_code=restored_content,
        )
    )

    llm = LLM()
    generate_code_modifications_response = await llm.chat(
        prompt=generate_code_modifications_message
    )
    print(generate_code_modifications_response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(start())
