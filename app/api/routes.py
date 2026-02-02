from fastapi import APIRouter

from app.api.deps import get_session_manager
from app.models.schemas import SessionRequest, SessionResponse


router = APIRouter()


@router.post("/token")
async def create_token(request: SessionRequest):
    session_manager = get_session_manager()
    
    session_id = f"{request.room_name}_{request.identity}"
    
    return {
        "session_id": session_id,
        "participant": request.identity,
        "room_name": request.room_name,
    }


@router.post("/recording/start/{room_name}/{participant}")
async def start_recording(room_name: str, participant: str):
    return {"success": True, "message": "Recording handled via WebSocket"}


@router.post("/recording/stop/{room_name}/{participant}")
async def stop_recording(room_name: str, participant: str):
    return {"success": True, "message": "Recording stopped via WebSocket"}


@router.get("/sessions/active")
async def get_active_sessions():
    session_manager = get_session_manager()
    sessions = session_manager.get_all_sessions()
    
    return {
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "participant": s.participant,
                "started_at": s.started_at.isoformat(),
                "duration_seconds": s.duration_seconds,
                "sample_rate": s.sample_rate,
                "channels": s.channels,
            }
            for s in sessions
        ]
    }


@router.get("/health")
async def health_check():
    session_manager = get_session_manager()
    active_count = len(session_manager.get_all_sessions())
    
    return {
        "status": "healthy",
        "active_sessions": active_count,
    }