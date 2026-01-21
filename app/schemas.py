from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Any

class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: Any | None = None

class Status(str, Enum):
    ok = "ok"
    warn = "warn"
    fail = "fail"

class ReadingIn(BaseModel):
    sensor_id: str = Field(min_length=1, max_length=64)
    ts: datetime | None = None  # optional; server will default if missing
    temperature_c: float = Field(ge=-50, le=150)  # typical sensor range
    humidity_pct: float = Field(ge=0, le=100)
    status: Status
