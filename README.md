# Healthcare Data Harmonization with Domain-Tuned LLMs (Hugging Face or Mock)

This project converts free-text clinical notes into **FHIR Bundles** (Patient, Condition, MedicationStatement) using a simple, reliable LLM extraction pipeline plus post-processing. It includes:

- **Providers:** Hugging Face Inference API **or** a free **Mock** provider (regex parser) for local dev
- **Strict JSON contract:** prompts enforce JSON → consistent post-processing
- **FHIR output:** minimal but valid Bundle using pydantic models
- **Evaluation:** field metrics (F1/RMSE), **bootstrap confidence intervals**, **slice-based** fairness (age/sex)
- **API:** FastAPI server for `/harmonize` endpoint
- **Batch:** script to process folders of `.txt` notes

> **Why not LangChain?** One call + strict schema keeps the pipeline lean and fast; you can swap providers later if needed.

---

## Directory structure

```text
llm-harmonizer/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .env.example
├─ Dockerfile
├─ src/
│  ├─ config.py                     # env config (provider/model/token)
│  ├─ prompts/templates.py          # system + user prompt template
│  ├─ llm/
│  │  ├─ provider.py                # abstract LLMProvider
│  │  ├─ hf_provider.py             # Hugging Face Inference API adapter
│  │  └─ mock_provider.py           # FREE local mock that parses notes
│  ├─ mapping/
│  │  ├─ fhir_models.py             # pydantic FHIR models (Bundle/Patient/...)
│  │  ├─ normalizer.py              # tiny SNOMED/RxNorm maps, freq normalization
│  │  └─ postprocess.py             # canonical JSON → FHIR Bundle builder
│  ├─ pipeline/harmonize.py         # orchestrates provider → parse → FHIR
│  └─ eval/
│     ├─ metrics.py                 # F1 for conditions/med names, dose RMSE
│     ├─ bootstrap_ci.py            # percentile CI for mean metric
│     └─ slicing.py                 # by-age/by-sex grouping
├─ app/
│  ├─ main.py                       # FastAPI app
│  ├─ models.py                     # request/response schemas
│  └─ routes.py                     # /health, /harmonize routes
├─ data/
│  ├─ synth/
│  │  ├─ generate.py                # synthetic notes + gold labels
│  │  ├─ notes.jsonl                # generated inputs (git-ignored)
│  │  └─ labels.jsonl               # generated gold (git-ignored)
│  └─ lookups/terminology.csv       # (optional) place for vocab
├─ scripts/
│  ├─ evaluate.py                   # runs pipeline on synth data, prints metrics
│  ├─ ingest_folder.py              # batch notes/*.txt → *.bundle.json
│  └─ peek_data.py                  # quick random data inspection (optional)
└─ tests/
   ├─ test_pipeline.py
   └─ test_eval.py
```

> **Note (macOS/Windows):** Ensure the folder is named exactly `scripts/` (no trailing spaces). If you accidentally created `scripts␠/`, rename it:  
> `git mv "scripts " scripts`

---

## Quickstart

### 1) Create & activate a venv
```bash
python3.11 -m venv .venv
source .venv/bin/activate
# Windows PowerShell:
# py -3.11 -m venv .venv; .\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```bash
python -m pip install --upgrade pip setuptools wheel
pip install --no-cache-dir -r requirements.txt
```

### 3) Configure provider (`.env`)
```bash
cp .env.example .env
```
Edit `.env`:

- **Free local demo (no external calls):**
  ```
  PROVIDER=mock
  ```

- **Hugging Face Inference API:**
  ```
  PROVIDER=hf
  HF_MODEL_ID=microsoft/Phi-3-mini-4k-instruct     # or another instruct model you’ve accepted
  HF_TOKEN=hf_********************************     # HF Settings → Access Tokens (Read)
  ```
  *Make sure you clicked **“Agree and access”** on the model page with the **same account** as the token.*

---

## Generate sample data

Create synthetic notes (inputs) and gold labels (truth):
```bash
python -m data.synth.generate --n 200
```

Outputs:
- `data/synth/notes.jsonl` (each line: `{"id", "note"}`)
- `data/synth/labels.jsonl` (each line: `{"id", "label"}`)

### Example notes (from `notes.jsonl`)
```
ID=94
NOTE=56 yo F with hyperlipidemia, asthma, depression. Rx: metformin 500 mg BID, sertraline 50 mg QD, lisinopril 10 mg QD.
------------------------------------------------------------
ID=25
NOTE=47 yo M with type 2 diabetes, depression, hyperlipidemia. Rx: atorvastatin 20 mg QD, sertraline 50 mg QD, albuterol 90 mcg PRN.
------------------------------------------------------------
ID=50
NOTE=60 yo F with depression, type 2 diabetes, hyperlipidemia. Rx: metformin 500 mg BID, albuterol 90 mcg PRN.
```

### Example gold label (from `labels.jsonl`)
```json
{
  "patient": {"age": 78, "sex": "F"},
  "conditions": [
    {"name": "asthma"},
    {"name": "type 2 diabetes"}
  ],
  "medications": [
    {"name": "atorvastatin", "dose": 20, "unit": "mg", "frequency": "QD"},
    {"name": "albuterol", "dose": 90, "unit": "mcg", "frequency": "PRN"}
  ]
}
```

---

## Evaluate offline

Compute dataset averages and 95% bootstrap CIs; also print slice metrics by age/sex.
```bash
python -m scripts.evaluate
```
Sample output (mock provider will be near‑perfect):
```json
{
  "condition_f1": 1.0,
  "condition_ci95": [1.0, 1.0],
  "med_name_f1": 1.0,
  "med_ci95": [1.0, 1.0],
  "dose_rmse": 0.0
}
{
  "slice_age": {"<40": 1.0, "40-60": 1.0, ">60": 1.0},
  "slice_sex": {"M": 1.0, "F": 1.0}
}
```

**Metrics explained**
- **condition_f1 / med_name_f1:** set‑based precision/recall/F1 over condition/medication names.
- **dose_rmse:** root mean squared error for numeric doses, only on overlapping meds with numeric doses.
- **bootstrap CIs:** percentile CI of the **mean** metric via resampling with replacement.
- **slice reports:** average metric per age bucket (`<40`, `40–60`, `>60`) and per sex (`M`, `F`).

---

## Run the API

Start the server:
```bash
uvicorn app.main:app --reload --port 8080
```
Open **Swagger** at http://localhost:8080/docs

**cURL example**
```bash
curl -X POST http://localhost:8080/harmonize \
  -H 'Content-Type: application/json' \
  -d '{"note":"54 yo F with hypertension. Rx: lisinopril 10 mg QD; metformin 500 mg BID."}'
```
Response contains a **FHIR Bundle** with Patient/Condition/MedicationStatement entries.

---

## Batch ingest (notes → bundles)
```bash
mkdir -p notes_in out_bundles
# add .txt files to notes_in/
python -m scripts.ingest_folder --input notes_in --output out_bundles
```

---

## Peek at random data (quick sanity)
Show a few random notes:
```bash
python - <<'PY'
import json, random
rows = [json.loads(l) for l in open('data/synth/notes.jsonl')]
for r in random.sample(rows, k=min(5,len(rows))):
    print(f"ID={r['id']}\nNOTE={r['note']}\n"+"-"*60)
PY
```

(There’s also an optional `scripts/peek_data.py` utility in this repo.)

---

## Provider details
- **Mock provider** (`PROVIDER=mock`): deterministic regex extractor. Great for free, fast iteration and for showing the full pipeline.
- **Hugging Face provider** (`PROVIDER=hf`): calls the specified model via Inference API. Ensure `HF_TOKEN` is valid and you’ve accepted the model’s terms.

---

## Troubleshooting

**401 Unauthorized (HF)**
- Check `.env` is loaded; probe in Python:
  ```py
  from src.config import settings
  print(settings.provider, settings.hf_model_id, (settings.hf_token or '')[:6]+'...')
  ```
- `curl -H "Authorization: Bearer $HF_TOKEN" https://api-inference.huggingface.co/models/$HF_MODEL_ID` → expect 200/503; 401 means bad token; 403 means terms not accepted.

**Import/package errors**
- Activate venv (`(.venv)` in prompt). Run from **project root**.
- Remove stale caches: `find . -name '__pycache__' -type d -print -exec rm -rf {} +`

**`scripts` package not found**
- Ensure folder name is exactly `scripts/` (no trailing space). Then run: `python -m scripts.evaluate`.

**All zeros for condition F1**
- If using the original mock (fixed outputs), restrict generator conditions to the same set, or use the smarter mock that parses the note text.

---

## Security & Git hygiene
- Keep secrets in `.env` (already in `.gitignore`). If you accidentally committed it:
  ```bash
  git rm --cached .env && git commit -m "chore: stop tracking .env"
  ```
- Use SSH or the right GitHub token per account to avoid push/identity mixups.

---

## Roadmap / Next steps
- JSON‑schema validation with retry on malformed LLM outputs
- Expand terminology maps; unit normalization (mg↔g) before dose RMSE
- Structured **Dosage.timing** instead of `text` frequency
- Add monitoring + drift checks for production

---

