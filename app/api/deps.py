from app.services.session import SessionManager
from app.services.transcription import TranscriptionService


_session_manager: SessionManager | None = None
_transcription_service: TranscriptionService | None = None


def init_services():
    global _session_manager, _transcription_service
    _session_manager = SessionManager()
    _transcription_service = TranscriptionService()


def get_session_manager() -> SessionManager:
    if _session_manager is None:
        raise RuntimeError("SessionManager not initialized")
    return _session_manager


def get_transcription_service() -> TranscriptionService:
    if _transcription_service is None:
        raise RuntimeError("TranscriptionService not initialized")
    return _transcription_service


async def cleanup_services():
    pass