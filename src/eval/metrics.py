from typing import List, Dict, Any, Optional

def _set(lst, key):
    return {x.get(key, "").lower() for x in lst}

def condition_f1(pred: List[Dict[str, Any]], gold: List[Dict[str, Any]]):
    pred_set = _set(pred, "name")
    gold_set = _set(gold, "name")
    
    if not pred_set and not gold_set:
        return 1.0
    
    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    pc = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rc = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (pc * rc) / (pc + rc) if (pc + rc) > 0 else 0.0
    return {"precision": pc, "recall": rc, "f1": f1}
    
def medication_f1(pred: List[Dict[str, Any]], gold: List[Dict[str, Any]]):
    return condition_f1([{"name" : m.get("name", "")} for m in pred], [{"name" : m.get("name", "")} for m in gold])

def dose_rmse(pred: List[Dict[str, Any]], gold: List[Dict[str, Any]]):
    import math
    gm = {m.get("name", "").lower(): m for m in gold}
    diffs = []
    for p in pred:
        name = p.get("name", "").lower()
        if name in gm and p.get("dose") is not None and gm[name].get("dose") is not None:
            diffs.append((p["dose"] - gm[name]["dose"])**2)
    if not diffs:
        return None
    return math.sqrt(sum(diffs)/len(diffs))