from pydantic import BaseModel, conint
from datetime import datetime
from typing import Optional

class FeedbackCreate(BaseModel):
    score: conint(ge=1, le=5)

class Feedback(BaseModel):
    id: int
    score: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True 

class FeedbackUpdate(BaseModel):
    score: Optional[conint(ge=1, le=5)] = None
