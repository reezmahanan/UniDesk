from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoticeCreate(BaseModel):
    title: str
    content: str
    tag: str = "General"
    audience: str = "ALL"
    is_published: bool = True
    expiry_date: Optional[datetime] = None

class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    tag: str
    audience: str
    is_published: bool
    publish_date: datetime
    expiry_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
