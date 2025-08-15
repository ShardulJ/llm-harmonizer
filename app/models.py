from pydantic import BaseModel

class HarmonizeRequest(BaseModel):
    note: str

class HarmonizeResponse(BaseModel):
    bundle: dict

