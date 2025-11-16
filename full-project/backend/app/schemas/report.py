from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional

class Status(str, Enum):
    pending = "pending"
    in_review = "in_review"
    resolved = "resolved"
    rejected = "rejected"

class Report(BaseModel):
    id: int
    reviewId: int
    reporterId: int
    reason: str
    status: Status
    createdAt: datetime
    processedAt: Optional[datetime] = None