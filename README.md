# ComplyAI (Week 1 MVP - GDPR First)

Local CLI prototype for contract/privacy document analysis:

- Extract clauses from PDF
- Match clauses to relevant GDPR articles (RAG)
- Score risk and identify issues
- Suggest improved clause text
- Save a structured JSON report

## Setup

```bash
cd complyai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure `.env`:

```env
OPENAI_API_KEY=...
MODEL_TEXT=gpt-4.1-mini
MODEL_EMBED=text-embedding-3-small
CHROMA_DIR=storage/chroma
REPORT_DIR=storage/reports
```

## Build GDPR index

```bash
python -m app.rag.build_index
```

## Run full analysis

```bash
python -m app.pipeline.run_pipeline --file data/samples/contracts/sample_vendor_agreement.pdf
```

## Output

Report JSON is written to:

- `storage/reports/<doc_hash>.json`

Includes:

- `clauses`
- `gdpr_matches`
- `risk_scores`
- `suggested_fixes`
- `executive_summary`

## Notes

- If `OPENAI_API_KEY` is not set, the pipeline still runs using deterministic local heuristics/fallback embeddings.
- `storage/chroma` is created automatically.
