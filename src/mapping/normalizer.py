import re
from typing import Optional

DRUG_MAP = {
    "metformin": {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975", "display": "Metformin"},
    "lisinopril": {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "29046", "display" : "Lisinopril"},
}

CONDITOIN_MAP = {
    "hypertension": {"system": "http://snomed.info/sct", "code": "38341003", "display": "Hypertensive disorder"},
    "type 2 diabetes": {"system": "http://snomed.info/sct", "code": "44054006", "display": "Type 2 diabetes mellitus"},
}

FREQ_MAP = {"qd": "QD", "bid": "BID", "tid": "TID"}

def drug_norm(name: str) -> Optional[dict]:
    name = name.lower().strip()
    return DRUG_MAP.get(name)

def condition_norm(name: str) -> Optional[dict]:
    name = name.lower().strip()
    return CONDITOIN_MAP.get(name)

def frequency_norm(freq: str) -> Optional[str]:
    freq = freq.lower().strip()
    return FREQ_MAP.get(freq)

def extract_age_sex(note:str):
    age = None
    sex = None
    m = re.search(r"(\b[MFmf]\b|\b(male|female)\b)", note)

    if m:
        s = m.group(0).lower()
        sex = "female" if s in ("f", "female") else "male"
    m = re.search(r"(\b\d{1,3})\s*(yo|y/o|years?\s*old)\b", note)
    if m:
        try: 
            age = int(m.group(1))
        except Exception:
            pass 
    return age, sex