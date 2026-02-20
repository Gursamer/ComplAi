from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv_if_present(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass
class Settings:
    openai_api_key: str
    model_text: str
    model_embed: str
    chroma_dir: str
    report_dir: str
    clause_top_k: int

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_dir)

    @property
    def report_path(self) -> Path:
        return Path(self.report_dir)


_load_dotenv_if_present()
settings = Settings(
    openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
    model_text=os.environ.get("MODEL_TEXT", "gpt-4.1-mini"),
    model_embed=os.environ.get("MODEL_EMBED", "text-embedding-3-small"),
    chroma_dir=os.environ.get("CHROMA_DIR", "storage/chroma"),
    report_dir=os.environ.get("REPORT_DIR", "storage/reports"),
    clause_top_k=int(os.environ.get("CLAUSE_TOP_K", "3")),
)
