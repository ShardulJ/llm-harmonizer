import httpx
from .provider import LLMProvider
from src.config import settings

class HFProvider(LLMProvider):
    def __init__(self, model_id:str | None = None, token: str | None = None):
        self.model_id = model_id or settings.hf_model_id
        self.token = token or settings.hf_token

        if not self.model_id:
            raise ValueError("HFProvider: hf_model_id is required")
        if not self.token:
            raise ValueError("HFProvider: hf_token is required")
        self.url = f"https://api-inference.huggingface.co/models/{self.model_id}"

        async def infer (self, system_prompt: str, user_prompt: str) -> str:
            prompt = f"[SYSTEM]\n{system_prompt}\n[USER]\n{user_prompt}\n[ASSISTANT]\n"
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "inputs": prompt,
                "parameters" : {
                    "max_new_tokens" : 512,
                    "temperature" : 0.1,
                    "return_full_text": False
                }    
            }

            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(self.url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                text = data[0]["generated_text"]
                return text.strip()
