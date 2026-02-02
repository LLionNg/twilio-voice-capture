from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class AudioFormat(str, Enum):
    PCM = "pcm"
    WAV = "wav"


@dataclass
class ActiveSession:
    session_id: str
    participant: str
    started_at: datetime
    sample_rate: int = 48000
    channels: int = 1
    language: str = "th-TH"
    
    pcm_path: str | None = None
    wav_path: str | None = None
    
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        return (datetime.utcnow() - self.started_at).total_seconds()


class SessionRequest(BaseModel):
    room_name: str
    identity: str


class SessionResponse(BaseModel):
    session_id: str
    participant: str
    status: str


class TranscriptMessage(BaseModel):
    text: str
    is_final: bool
    sentence_count: int = 0


class FormUpdateMessage(BaseModel):
    form_data: dict[str, Any]
    updated_fields: list[str]
    batch_number: int


class StatusMessage(BaseModel):
    status: str
    message: str
    session_id: str | None = None


class WebSocketMessage(BaseModel):
    type: str
    data: dict[str, Any] | None = None