from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from starlette.concurrency import run_in_threadpool

from backend.app.dependencies import get_resume_service
from backend.app.schemas.resume import ResumeUploadResponse
from backend.app.services.resume_service import ResumeService


router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    service: ResumeService = Depends(get_resume_service),
) -> dict:
    return await run_in_threadpool(
        service.parse_upload,
        filename=file.filename or "resume",
        content_type=file.content_type or "application/octet-stream",
        stream=file.file,
    )
