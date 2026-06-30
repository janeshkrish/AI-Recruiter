from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import BinaryIO
from zipfile import ZipFile

from backend.app.core.errors import AppError


KNOWN_SKILLS = (
    "python",
    "machine learning",
    "deep learning",
    "nlp",
    "retrieval",
    "ranking",
    "recommendation",
    "embeddings",
    "vector search",
    "faiss",
    "qdrant",
    "pinecone",
    "weaviate",
    "milvus",
    "elasticsearch",
    "opensearch",
    "fastapi",
    "django",
    "flask",
    "spark",
    "airflow",
    "kubernetes",
    "docker",
    "mlflow",
)


class ResumeService:
    """Safely handles uploaded resumes without executing uploaded content."""

    def __init__(self, max_upload_bytes: int) -> None:
        self.max_upload_bytes = max_upload_bytes

    def parse_upload(self, *, filename: str, content_type: str, stream: BinaryIO) -> dict:
        raw = stream.read(self.max_upload_bytes + 1)
        if len(raw) > self.max_upload_bytes:
            raise AppError("Uploaded file exceeds size limit.", status_code=413, code="UPLOAD_TOO_LARGE")

        suffix = Path(filename).suffix.lower()
        with tempfile.TemporaryDirectory(prefix="ai-recruiter-upload-") as tmp:
            isolated_path = Path(tmp) / Path(filename).name
            isolated_path.write_bytes(raw)
            text, warnings = self._extract_text(isolated_path, suffix, content_type)

        normalized = text.lower()
        skills = sorted({skill for skill in KNOWN_SKILLS if skill in normalized})
        return {
            "filename": filename,
            "content_type": content_type or "application/octet-stream",
            "size_bytes": len(raw),
            "text_preview": re.sub(r"\s+", " ", text).strip()[:800],
            "extracted_skills": skills,
            "warnings": warnings,
        }

    def _extract_text(self, path: Path, suffix: str, content_type: str) -> tuple[str, list[str]]:
        warnings: list[str] = []
        allowed_suffixes = {".txt", ".md", ".csv", ".docx", ".pdf"}
        if suffix not in allowed_suffixes and not content_type.startswith("text/"):
            raise AppError("Unsupported resume file type.", status_code=400, code="UNSUPPORTED_RESUME_TYPE")
        if suffix in {".txt", ".md", ".csv"} or content_type.startswith("text/"):
            return path.read_text(encoding="utf-8", errors="ignore"), warnings
        if suffix == ".docx":
            try:
                with ZipFile(path) as z:
                    xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
                text = re.sub(r"<[^>]+>", " ", xml)
                return text, warnings
            except Exception:
                warnings.append("DOCX text extraction failed; file was accepted but not parsed.")
                return "", warnings
        if suffix == ".pdf":
            warnings.append("PDF upload accepted. Install a PDF parser for full text extraction in production.")
            return "", warnings
        warnings.append("Unsupported resume type for text extraction; file was isolated and discarded.")
        return "", warnings
