from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.analyze import router as analyze_router
from app.api.routes.reports import router as reports_router


app = FastAPI(
    title="ComplyAI API",
    version="0.1.0",
    description="API wrapper for ComplyAI GDPR analysis pipeline.",
)

app.include_router(analyze_router)
app.include_router(reports_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

