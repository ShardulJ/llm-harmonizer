import random 
from typing import Callable, List, Dict

def bootstrap_ci(pairs: List[Dict], metric_fn: Callable[[Dict], float], n_boot: int = 1000, alpha: float = 0.05):
    stats = []
    n = len(pairs)
    for _ in range(n_boot):
        sample = [random.choice(pairs) for _ in range(n)]
        vals = [metric_fn(x) for x in sample]
        stats.append(sum(vals)/len(vals) if vals else 0.0)
    stats.sort()
    lo = stats[int((alpha/2)*n_boot)]
    hi = stats[int((1 - alpha/2)*n_boot)]
    return lo, hi
