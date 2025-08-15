from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def infer(self, system_prompt: str, user_prompt: str) -> str:
        ...