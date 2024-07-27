import httpx
from agent.config import settings
from llama_index.llms.ollama import Ollama
from typing import Dict


async def is_url_reachable(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.status_code == 200
    except httpx.RequestError:
        return False


class LLMInitializer:
    def __init__(self):
        self.base_url = None
        self.model = None
        self.context_window = None
        self.request_timeout = 600

    async def initialize(self):
        fallback = await is_url_reachable(settings.llm.base_url)

        self.base_url = (
            settings.llm.base_url if fallback else settings.fallback_llm.base_url
        )
        self.model = settings.llm.model if fallback else settings.fallback_llm.model
        self.context_window = (
            settings.llm.context_window
            if fallback
            else settings.fallback_llm.context_window
        )

        print(
            f"Using {self.base_url} with {self.model} of context window {self.context_window} in request_timeout {self.request_timeout} s."
        )

        return Ollama(
            model=self.model,
            base_url=self.base_url,
            context_window=self.context_window,
            request_timeout=self.request_timeout,
            json_mode=True,
        )

    @staticmethod
    def print_final_response_details(raw: Dict[str, str]):
        # 提取相关信息
        total_duration_ns = raw.get("total_duration")
        prompt_eval_count = raw.get("prompt_eval_count")
        eval_count = raw.get("eval_count")
        eval_duration = raw.get("eval_duration")

        # 转换 Total Duration 为秒
        total_duration_s = total_duration_ns / 1e9 if total_duration_ns else 0

        # 计算响应生成速度（tokens/s）
        tokens_per_second = eval_count / eval_duration * 1e9 if eval_duration else 0

        print("\nExtracted Response Details:")
        print(f"Time spent generating the response: {total_duration_s:.2f} seconds")
        print(f"Number of tokens in the prompt: {prompt_eval_count}")
        print(f"Number of tokens in the response: {eval_count}")
        print(f"Tokens per Second: {tokens_per_second:.2f} tokens/s")


if __name__ == "__main__":

    async def main():
        initializer = LLMInitializer()
        llm = await initializer.initialize()

    import asyncio

    asyncio.run(main())
