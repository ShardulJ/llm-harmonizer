from collections import defaultdict
from typing import List, Dict

def slice_by_age(pairs: List[Dict]):
    buckets = {"<40": [], "40-60": [], ">60": []}
    for p in pairs:
        age = p.get("age")
        if age is None:
            continue
        if age < 40:
            buckets["<40"].append(p)
        elif 40 <= age <= 60:
            buckets["40-60"].append(p)
        else:
            buckets[">60"].append(p)
    return buckets

def slice_by_sex(pairs: List[Dict]):
    out = defaultdict(list)
    for p in pairs:
        s = p.get("demo", {}).get("sex", "U")
        out[s].append(p)
    return out 

