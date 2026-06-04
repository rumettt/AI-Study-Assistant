from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    content_type: str
    size_bytes: int
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    id: str
    status: str
    error_message: str | None = None
    chunk_count: int = 0
    processed_at: datetime | None = None

    model_config = {"from_attributes": True}
