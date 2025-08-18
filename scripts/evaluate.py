from collections import OrderedDict
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
    notes = [json.loads(l) for l in open("./data/synthetic/notes.json")] 
    labels = {json.loads(l)["id"]: json.loads(l)["label"] for l in open("./data/synthetic/labels.json")}

    pairs: List[Dict[str, Any]] = []
    for note in notes:
        gold = labels[note["id"]]
        bundle = await harmonize(note["note"])
        pred = bundle_to_label(bundle)
        demo = {"age": gold.get("patient", {}).get("age"), "sex": gold.get("patient", {}).get("sex")}
        pairs.append({"id": note["id"], "gold": gold, "pred": pred, "demo": demo})

        def cond_metric(p):
            return float(condition_f1(p["pred"].get("conditions", []), p["gold"].get("conditions", []))["f1"])
        
        def med_metric(p):
            return medication_f1(p["pred"].get("meds", []), p["gold"].get("meds", []))
        
        cond_f1 = sum(cond_metric(p) for p in pairs) / len(pairs)
        med_f1 = sum(med_metric(p) for p in pairs) / len(pairs)
        condition_ci = bootstrap_ci(pairs, cond_metric)
        medication_ci = bootstrap_ci(pairs, med_metric)

        rmse_vals = [dose_rmse(p["pred"].get("meds", []), p["gold"].get("meds", [])) for p in pairs]
        rmse_vals = [v for v in rmse_vals if v is not None]
        dose_rmse_vals = sum(rmse_vals) / len(rmse_vals) if rmse_vals else 0.0

        print({
            "condition_f1": round(cond_f1, 4),
            condition_ci: [round(condition_ci[0], 4), round(condition_ci[1], 4)],
            "medication_f1": round(med_f1, 4),
            medication_ci: [round(medication_ci[0], 4), round(medication_ci[1], 4)],
            "dose_rmse": round(dose_rmse_vals, 4)
        })

        from collections import defaultdict
        by_age = slice_by_age(pairs)
        age_report = OrderedDict()
        for k, vs in by_age.items():
            if not vs: continue
            age_report[k] = round(sum(cond_metric(p) for p in vs) / len(vs), 4)

        by_sex = slice_by_sex(pairs)
        sex_report = OrderedDict()
        for k, vs in by_sex.items():
            if not vs: continue
            sex_report[k] = round(sum(cond_metric(p) for p in vs) / len(vs), 4)

        print({"slice age": age_report, "slice sex": sex_report})


if __name__ == "__main__":
    asyncio.run(main())