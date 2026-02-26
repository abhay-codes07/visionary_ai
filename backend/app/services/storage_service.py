from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.schemas.vision import VisionUploadResponse


class StorageService:
    def __init__(self, upload_root: str = "/tmp/visionary_uploads") -> None:
        self.upload_root = Path(upload_root)
        self.upload_root.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile, media_type: str) -> VisionUploadResponse:
        upload_id = str(uuid4())
        safe_name = file.filename or f"{upload_id}.bin"
        destination = self.upload_root / f"{upload_id}_{safe_name}"

        content = await file.read()
        destination.write_bytes(content)

        return VisionUploadResponse(
            upload_id=upload_id,
            filename=safe_name,
            media_type=media_type,  # validated in API layer
            content_type=file.content_type or "application/octet-stream",
            size_bytes=len(content),
            storage_uri=str(destination.as_posix()),
            uploaded_at=datetime.now(timezone.utc),
        )

