# Healthcare Data Harmonization with Domain-Tuned LLMs

This is a **GenAI (LLM) extraction service**: it converts free‑text clinical notes into **FHIR‑compliant Bundles** (Patient, Condition, MedicationStatement), with **slice‑based evaluation**, **bootstrap confidence intervals**, and a **FastAPI** API. It uses the **Hugging Face Inference API** (free tier, rate‑limited) or a **mock** provider so you can run everything free.

## What & Why
**Goal:** Robustly extract a small, well‑defined JSON from messy notes, normalize it, and emit FHIR. Keeping output strict JSON makes downstream post‑processing deterministic and evaluation easy.