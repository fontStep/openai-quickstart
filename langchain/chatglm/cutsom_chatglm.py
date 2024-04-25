import json
import logging
from typing import Any, List, Optional, Union

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.pydantic_v1 import Field

from langchain_community.llms.utils import enforce_stop_tokens
import os

logger = logging.getLogger(__name__)

api_key=os.getenv("ZHIPUAI_API_KEY")


HEADERS = {"Content-Type": "application/json","Authorization": f"Bearer {api_key}"}
DEFAULT_TIMEOUT = 30


def _convert_message_to_dict(message: BaseMessage) -> dict:
    if isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    elif isinstance(message, FunctionMessage):
        message_dict = {"role": "function", "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")
    return message_dict

class CutsomChatGLM3(LLM):
    """ChatGLM3 LLM service."""

    model_name: str = Field(default="glm-3-turbo", alias="model")
    endpoint_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    """Endpoint URL to use."""
    model_kwargs: Optional[dict] = None
    """Keyword arguments to pass to the model."""
    max_tokens: int = 1024
    """Max token allowed to pass to the model."""
    temperature: float = 0.1
    """LLM model temperature from 0 to 10."""
    top_p: float = 0.7
    """Top P for nucleus sampling from 0 to 1"""
    prefix_messages: List[BaseMessage] = Field(default_factory=list)
    """Series of messages for Chat input."""
    streaming: bool = False
    """Whether to stream the results or not."""
    http_client: Union[Any, None] = None
    timeout: int = DEFAULT_TIMEOUT

    @property
    def _llm_type(self) -> str:
        return "chat_glm_3"

    @property
    def _invocation_params(self) -> dict:
        
        """Get the parameters used to invoke the model."""
        params = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.streaming,
        }
        return {**params, **(self.model_kwargs or {})}

    @property
    def client(self) -> Any:
        import httpx

        return self.http_client or httpx.Client(timeout=self.timeout)

    def _get_payload(self, prompt: str) -> dict:
        params = self._invocation_params
        logger.warn(f"ChatGLM3 prompt: {prompt}")
        
        sections = prompt.split("Human:")
        messages =[]
        for section in sections:
            if section.startswith("System:"):
                system_data = section.replace("System:", "").strip()
                messages.append(SystemMessage(content=system_data))
            else:
                human_data = section.strip()
                messages.append(HumanMessage(content=human_data))
        
        messages = self.prefix_messages + messages
        logger.warn(f"ChatGLM3 messages: {messages}")
        params.update(
            {
                "messages": [_convert_message_to_dict(m) for m in messages],
            }
        )
        return params

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call out to a ChatGLM3 LLM inference endpoint.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                response = chatglm_llm("Who are you?")
        """
        import httpx

        payload = self._get_payload(prompt)
        logger.warn(f"ChatGLM3 payload: {payload}")

        try:
            logger.warn(f"ChatGLM3 HEADERS: {HEADERS}")
            response = self.client.post(
                self.endpoint_url, headers=HEADERS, json=payload
            )
        except httpx.NetworkError as e:
            raise ValueError(f"Error raised by inference endpoint: {e}")

        logger.warn(f"ChatGLM3 response: {response.json()}")

        if response.status_code != 200:
            raise ValueError(f"Failed with response: {response}")

        try:
            parsed_response = response.json()

            if isinstance(parsed_response, dict):
                content_keys = "choices"
                if content_keys in parsed_response:
                    choices = parsed_response[content_keys]
                    if len(choices):
                        text = choices[0]["message"]["content"]
                else:
                    raise ValueError(f"No content in response : {parsed_response}")
            else:
                raise ValueError(f"Unexpected response type: {parsed_response}")

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error raised during decoding response from inference endpoint: {e}."
                f"\nResponse: {response.text}"
            )

        if stop is not None:
            text = enforce_stop_tokens(text, stop)

        return text
    
    
