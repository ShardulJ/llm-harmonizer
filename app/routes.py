from fastapi import APIRouter
from src.pipeline.harmonize import harmonize
from .models import HarmonizeRequest, HarmonizeResponse

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/harmonize", response_model=HarmonizeResponse)
async def harmonize(req: HarmonizeRequest):
    bundle = await harmonize(req.note)
    return {"bundle": bundle}

