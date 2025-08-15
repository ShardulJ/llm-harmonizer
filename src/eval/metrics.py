from typing import List, Dict, Any, Optional

def _set(lst, key):
    return {x.get(key, "").lower() for x in lst}

def condition_f1(pred: List[Dict[str, Any]], gold: List[Dict[str, Any]]):
    pred_set = _set(pred, "name")
    gold_set = _set(gold, "name")
    
    if not pred_set and not gold_set:
        return 1.0
    
    tp = len(pred_set & gold_set)
    if tp == 0:
        return 0.0
    
    precision = tp / len(pred_set) if pred_set else 0.0
    recall = tp / len(gold_set) if gold_set else 0.0
    
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0