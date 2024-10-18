from agent.constans.default import (
    test_problem_statement,
    test_target_repository_language,
)
from agent.constans.self_retrieval import self_retrieval_prompt_template
from agent.llm import LLM
from agent.constans.problem_set_model import ProblemSet
from agent.constans.self_retrieval import test_self_retrieval_prompt_output


async def start():
    self_retrieval_message = self_retrieval_prompt_template.format_messages(
        github_issue_description=test_problem_statement,
        count_of_exemplars=2,
        target_repository_language=test_target_repository_language,
    )

    llm = LLM()
    self_retrieval_response = await llm.chat(prompt=self_retrieval_message)

    problem_set = ProblemSet.model_validate_json(self_retrieval_response)
    print(problem_set.model_dump_json(indent=4))


if __name__ == "__main__":
    import asyncio

    asyncio.run(start())
