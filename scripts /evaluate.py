import json
import asyncio
from typing import Dict, Any, List
from src.pipeline.harmonize import harmonize
from src.eval.metrics import condition_f1, medication_f1, dose_rmse
from src.eval.bootstrap_ci import bootstrap_ci
from src.eval.slicing import slice_by_age, slice_by_sex

def bundle_to_label(bundle: Dict[str, Any]) -> Dict[str, Any]:
    out = {"patient": {}, "conditions": [], "med": []}
    for e in bundle.get("entry", []):
        r = e.get("resource", {})
        rt = r.get("resourceType", "")
        if rt == "Patient":
            if r.get("gender"):
                out["patient"]["sex"] = r["gender"][0].upper()
        elif rt == "Condition":
            coding = r.get("code", {}).get("coding", [])
            if coding:
                out["conditions"].append({"name": coding[0].get("display", "")})
        elif rt == "MedicationRequest":
            coding = r.get("medicationCodeableConcept", {}).get("coding", [])
            name = coding[0].get("display", "") if coding else ""
            dose = None
            try:
                dr = r.get("dosage", [])[0].get("doseAndRate", [])
                dose = dr.get("value")
            except Exception:
                pass 
            out["meds"].append({"name": name, "dose": dose})
    return out

async def main():
    pass 

if __name__ == "__main__":
    asyncio.run(main())