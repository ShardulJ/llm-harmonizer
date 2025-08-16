import json
import asyncio
from typing import Dict, Any, List
from src.pipeline.harmonize import harmonize
from src.eval.metrics import condition_f1, medication_f1, dose_rmse
from src.eval.bootstrap_ci import bootstrap_ci
from src.eval.slicing import slice_by_age, slice_by_sex

def bundle_to_label():
    pass 

async def main():
    pass 

if __name__ == "__main__":
    asyncio.run(main())