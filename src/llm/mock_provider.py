import json
from .provider import LLMProvider

EXAMPLE_OUTPUT = {
    "patient": {"age": 54, "sex": "F"},
    "conditions": [
        {"name": "hypertension"},
        {"name": "type 2 diabetes"}
    ],
    "medications": [
        {"name": "metformin", "dose": 500, "unit": "mg", "frequency": "BID"},
        {"name": "lisinopril", "dose": 10, "unit": "mg", "frequency": "QD"}
    ],
    "encounter_date": "2024-08-12"
}

class MockProvider(LLMProvider):
    async def infer(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps(EXAMPLE_OUTPUT)