import time
from typing import List, Dict, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

from smolagents import OpenAIServerModel, Tool, ChatMessage
from torch.fx.passes.reinplace import reinplace


# class SleepPerLastTokenOpenAIServerModel(OpenAIServerModel):
#     def __init__(self, sleep_factor: float = 0.01, **kwargs):
#         super().__init__(**kwargs)
#         self.sleep_factor = sleep_factor
#
#     def __call__(
#         self,
#         messages: List[Dict[str, str]],
#         stop_sequences: Optional[List[str]] = None,
#         grammar: Optional[str] = None,
#         tools_to_call_from: Optional[List[Tool]] = None,
#         **kwargs,
#     ) -> ChatMessage:
#         if self.last_input_token_count is not None:
#             sleep_time = (
#                 self.last_input_token_count + self.last_output_token_count
#             ) * self.sleep_factor
#             print(f"Sleeping for {sleep_time:.2f} seconds...")
#             time.sleep(sleep_time)
#
#         return super().__call__(
#             messages, stop_sequences, grammar, tools_to_call_from, **kwargs
#         )

class ExponentialBackoffOpenAIServerModel(OpenAIServerModel):
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List[Tool]] = None,
        **kwargs,
    ) -> ChatMessage:
        result = super().__call__(
            messages, stop_sequences, grammar, tools_to_call_from, **kwargs
        )
        if (result.content is None) or result.content.strip() == "":
            raise ValueError("Empty response")
        return result
