from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.pipeline.run_pipeline import run


router = APIRouter(tags=["analyze"])


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_path: Path | None = None
    try:
        payload = await file.read()
        if not payload:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(payload)
            tmp_path = Path(tmp.name)

        report_path = Path(run(str(tmp_path)))
        if not report_path.exists():
            raise HTTPException(status_code=500, detail="Report file was not generated.")

        report_json = json.loads(report_path.read_text(encoding="utf-8"))
        report_json["source_file"] = filename
        report_path.write_text(json.dumps(report_json, indent=2), encoding="utf-8")
        return report_json
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
