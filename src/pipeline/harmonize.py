import json
from src.config import settings
from src.prompts.templates import USER_PROMPT_TEMPLATE, SYSTEM_PROMPT
from src.llm.hf_provider import HFProvider
from src.mapping.normalizer import extract_age_sex
from src.mapping.postprocess import to_fhir_bundle

async def get_provider():
    if settings.provider == "hf" and settings.hf_token and settings.hf_model_id:
        return HFProvider()
    return None

async def harmonize(note_text: str) -> dict:
    provider = await get_provider()
    user_prompt = USER_PROMPT_TEMPLATE + note_text
    raw = await provider.infer(SYSTEM_PROMPT, user_prompt)

    try:
        parsed = json.loads(raw)
    except Exception:
        age, sex = extract_age_sex(note_text)
        parsed = {"patient": {"age": age, "sex": sex}, "conditions": [], "med": []}

    bundle = to_fhir_bundle(parsed)
    return bundle.model_dump() if bundle else {}