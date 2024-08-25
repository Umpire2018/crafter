import httpx
import asyncio
from agent.config import settings
from typing import List, Dict
from loguru import logger
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.llms.ollama import Ollama  
from llama_index.llms.openai_like import OpenAILike
from agent.constans.default import default_template

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

    async def chat(self,  messages: str, **kwargs):
        if self.ollama_is_reachable is None:
            self.ollama_is_reachable = await is_url_reachable(settings.ollama.base_url)
            if self.ollama_is_reachable:
                logger.success(f"Using Ollama Endpoint.")
            else:
                logger.success(f"Using OpenAILike Endpoint.")

        n = kwargs.pop("n", 1)  # Extract 'n' from kwargs, default to 1 if not provided
        temperature = 0 if n == 1 else 0.8

        if self.ollama_is_reachable:
            return await self._chat_with_ollama(messages, temperature, **kwargs)
        else:
            return await self._chat_with_openai_like(messages, n, temperature, **kwargs)
        
    async def _chat_with_ollama(self, prompt: str, temp: float, **kwargs) :
        if self.llm is None:
            self.llm = Ollama(
                model=settings.ollama.model,
                base_url=settings.ollama.base_url,
                context_window=settings.ollama.context_window,
                request_timeout=settings.ollama.request_timeout,
                json_mode=True
            )
        
        async def fetch_response() -> str:
            messages = default_template.format_messages(prompt=prompt)

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

    async def _chat_with_openai_like(self, prompt: str, n: int, temp: float, **kwargs):
        if self.llm is None:
            self.llm = OpenAILike(
                model=settings.openai_like.model,
                api_base=settings.openai_like.api_base,
                api_key=settings.openai_like.api_key,
                is_chat_model=True,
                response_format={ "type": "json_object" },
            )

        async def fetch_response() -> str | List[str]:
            messages = default_template.format_messages(prompt=prompt)

            response = await self.llm.achat(
                messages=messages, temperature=temp, n=n, **kwargs
            )
            logger.info(f"Raw Response from OpenAI-like at temperature {temp}: {response.raw}")

            if len(response.raw.choices) == 1:
                return response.message.content

            return [str(choice.message.content) for choice in response.raw.choices]

        initial_result = await fetch_response()

        if isinstance(initial_result, str) and n > 1:
            additional_tasks = [fetch_response() for _ in range(n - 1)]
            additional_results = await asyncio.gather(*additional_tasks)
            return [initial_result] + additional_results

        return initial_result