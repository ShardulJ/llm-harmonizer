import asyncio 
from src.pipeline.harmonize import harmonize

async def _run():
    note = "47 yo M with diabetes and hypertension, on metformin 500mg BID and lisinopril 10mg daily."
    b = await harmonize(note)
    assert b["resourceType"] == "Bundle"
    assert any(e for e in b["entry"] if e["resource"]["resourceType"] == "Patient")

def test_pipeline():
    asyncio.run(_run())
