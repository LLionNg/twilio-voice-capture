import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict

from loguru import logger

from app.core.config import get_settings
from app.models.schemas import ActiveSession
from app.services.audio import StreamBuffer


class SessionManager:
    
    def __init__(self):
        self.settings = get_settings()
        self.active_sessions: Dict[str, ActiveSession] = {}
        self.audio_buffers: Dict[str, StreamBuffer] = {}
        self._lock = asyncio.Lock()
        
        Path(self.settings.output_dir).mkdir(parents=True, exist_ok=True)
    
    async def create_session(
        self,
        session_id: str,
        participant: str,
        sample_rate: int = 48000,
        channels: int = 1,
        language: str = "th-TH",
    ) -> ActiveSession:
        async with self._lock:
            session = ActiveSession(
                session_id=session_id,
                participant=participant,
                started_at=datetime.utcnow(),
                sample_rate=sample_rate,
                channels=channels,
                language=language,
            )
            
            self.active_sessions[session_id] = session
            self.audio_buffers[session_id] = StreamBuffer(sample_rate, channels)
            
            logger.info(f"Session created: {session_id} ({participant})")
            return session
    
    async def add_audio_chunk(self, session_id: str, chunk: bytes) -> None:
        buffer = self.audio_buffers.get(session_id)
        if buffer:
            buffer.add_chunk(chunk)
    
    async def end_session(self, session_id: str) -> bool:
        async with self._lock:
            session = self.active_sessions.get(session_id)
            buffer = self.audio_buffers.get(session_id)
            
            if not session or not buffer:
                return False
            
            try:
                output_dir = Path(self.settings.output_dir)
                filename = f"{session.participant}_{session_id}.wav"
                filepath = output_dir / filename
                
                buffer.save_to_wav(filepath)
                
                duration = session.duration_seconds
                logger.info(
                    f"Session ended: {session_id} "
                    f"(duration: {duration:.1f}s, file: {filepath})"
                )
                
                del self.active_sessions[session_id]
                del self.audio_buffers[session_id]
                
                return True
            
            except Exception as e:
                logger.error(f"Failed to end session {session_id}: {e}")
                return False
    
    def get_session(self, session_id: str) -> ActiveSession | None:
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> list[ActiveSession]:
        return list(self.active_sessions.values())