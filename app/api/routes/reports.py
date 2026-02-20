from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import settings


router = APIRouter(tags=["reports"])


def _report_path(report_id: str) -> Path:
    return settings.report_path / f"{report_id}.json"


@router.get("/reports/{report_id}")
def get_report(report_id: str) -> dict:
    path = _report_path(report_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/reports")
def list_reports() -> dict:
    reports_dir = settings.report_path
    reports_dir.mkdir(parents=True, exist_ok=True)

    items = []
    for path in sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        report_id = path.stem
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            source_file = payload.get("source_file", "")
        except Exception:
            source_file = ""

        items.append(
            {
                "id": report_id,
                "source_file": source_file,
                "path": str(path),
            }
        )

    return {"count": len(items), "reports": items}

