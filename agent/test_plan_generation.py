from agent.constans.default import (
    test_problem_statement,
    test_target_repository_language,
)
from agent.constans.plan_generation import (
    plan_generation_prompt_template,
    confidence_generation_template,
)
from agent.llm import LLM
from agent.constans.problem_set_model import ProblemSet
from agent.constans.self_retrieval import test_self_retrieval_prompt_output


async def start():
    problem_set = ProblemSet.model_validate_json(test_self_retrieval_prompt_output)
    llm = LLM()

    for problem in problem_set.problems:
        plan_generation_prompt_message = (
            plan_generation_prompt_template.format_messages(
                problem_description=problem.description,
                planning_of_exemplar=problem.planning,
                retrieved_algorithm=problem_set.algorithm,
                original_problem=test_problem_statement,
            )
        )

        plan_generation_response = await llm.chat(prompt=plan_generation_prompt_message)
        print(plan_generation_response)

        confidence_generation_message = confidence_generation_template.format_messages(
            target_repository_language=test_target_repository_language,
            original_problem=test_problem_statement,
            planning_of_original_problem=plan_generation_response,
        )
        confidence_generation_response = await llm.chat(
            prompt=confidence_generation_message
        )

        print(confidence_generation_response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(start())
