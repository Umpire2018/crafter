import httpx
import asyncio
from typing import List, Dict
from loguru import logger
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.base.llms.types import ChatMessage
from agent.constans.default import default_template
from agent.config import settings


async def is_url_reachable(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.status_code == 200
    except httpx.RequestError:
        return False


class LLM:
    def __init__(self) -> None:
        self.llm: FunctionCallingLLM = None
        self.ollama_is_reachable: bool | None = None

    async def chat(self, prompt: str | ChatMessage, **kwargs):
        if self.ollama_is_reachable is None:
            try:
                self.ollama_is_reachable = await is_url_reachable(
                    settings.ollama.base_url
                )
                if self.ollama_is_reachable:
                    logger.success(f"Using Ollama Endpoint.")
                else:
                    logger.success(f"Using OpenAILike Endpoint.")
            except AttributeError:
                logger.success(f"Using OpenAILike Endpoint.")
                self.ollama_is_reachable = False

        # 回答输出个数
        n = kwargs.pop("n", 1)  # Extract 'n' from kwargs, default to 1 if not provided
        # 采样温度，控制输出的随机性，必须为正数取值范围是：[0.0, 1.0]，GLM默认值为0.95。
        temperature = 0 if n == 1 else settings.llm.openai_like.temperature

        if self.ollama_is_reachable:
            return await self._chat_with_ollama(
                prompt=prompt, n=n, temp=temperature, **kwargs
            )
        else:
            return await self._chat_with_openai_like(
                prompt=prompt, n=n, temp=temperature, **kwargs
            )

    async def _chat_with_ollama(
        self, prompt: str | ChatMessage, n: int, temp: float, **kwargs
    ):
        if self.llm is None:
            self.llm = Ollama(
                model=settings.ollama.model,
                base_url=settings.ollama.base_url,
                context_window=settings.ollama.context_window,
                request_timeout=settings.ollama.request_timeout,
                json_mode=True,
            )

        async def fetch_response() -> str:
            if isinstance(prompt, str):
                messages = default_template.format_messages(prompt=prompt)
            else:
                messages = prompt

            response = await self.llm.achat(
                messages=messages, temperature=temp, **kwargs
            )
            logger.info(f"Response: {response.message.content}")

            LLM._print_final_response_details(raw=response.raw)
            return response.message.content

        initial_result = await fetch_response()

        if n > 1:
            additional_tasks = [fetch_response() for _ in range(n - 1)]
            additional_results = await asyncio.gather(*additional_tasks)
            return [initial_result] + additional_results

        return initial_result

    @staticmethod
    def _print_final_response_details(raw: Dict[str, str]):
        total_duration_ns = raw.get("total_duration")
        prompt_eval_count = raw.get("prompt_eval_count")
        eval_count = raw.get("eval_count")
        eval_duration = raw.get("eval_duration")

        total_duration_s = total_duration_ns / 1e9 if total_duration_ns else 0
        tokens_per_second = eval_count / eval_duration * 1e9 if eval_duration else 0

        logger.info(f"""
        Extracted Response Details:
        Time spent generating the response: {total_duration_s:.2f} seconds
        Number of tokens in the prompt: {prompt_eval_count}
        Number of tokens in the response: {eval_count}
        Tokens per Second: {tokens_per_second:.2f} tokens/s
        """)

    async def _chat_with_openai_like(
        self, prompt: str | ChatMessage, n: int, temp: float, **kwargs
    ):
        if self.llm is None:
            self.llm = OpenAILike(
                model=settings.llm.openai_like.model,
                api_base=settings.llm.openai_like.api_base,
                api_key=settings.secrets.api_key,
                is_chat_model=True,
                response_format={"type": "json_object"},
            )

        async def fetch_response() -> str | List[str]:
            if isinstance(prompt, str):
                messages = default_template.format_messages(prompt=prompt)
            else:
                messages = prompt

            # 模型输出的最大token数，GLM最大输出为4095，默认值为1024。
            max_tokens = kwargs.pop("max_tokens", settings.llm.openai_like.max_tokens)

            response = await self.llm.achat(
                messages=messages, temperature=temp, n=n, max_tokens=max_tokens, **kwargs
            )
            logger.info(
                f"Request parameters: temperature={temp}, prompt_tokens={response.raw.usage.prompt_tokens}. Response parameters: completion_tokens={response.raw.usage.completion_tokens}"
            )

            if len(response.raw.choices) == 1:
                return response.message.content

            return [str(choice.message.content) for choice in response.raw.choices]

        initial_result = await fetch_response()

        if isinstance(initial_result, str) and n > 1:
            additional_tasks = [fetch_response() for _ in range(n - 1)]
            additional_results = await asyncio.gather(*additional_tasks)
            return [initial_result] + additional_results

        return initial_result
