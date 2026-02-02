import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.models.schemas import StatusMessage


router = APIRouter()


@router.websocket("/ws/audio")
async def websocket_audio(
    websocket: WebSocket,
    language: str = "th-TH",
    sr: int = 48000,
    ch: int = 1,
):
    from app.api.deps import get_session_manager, get_transcription_service
    
    await websocket.accept()
    
    session_id = str(id(websocket))
    participant = f"user_{session_id[-8:]}"
    
    session_manager = get_session_manager()
    transcription = get_transcription_service()
    
    logger.info(f"WebSocket connected: {session_id} (sr={sr}, ch={ch}, lang={language})")
    
    await websocket.send_json({
        "type": "status",
        "data": StatusMessage(
            status="connected",
            message=f"Connected: {session_id}",
            session_id=session_id,
        ).model_dump()
    })
    
    await session_manager.create_session(
        session_id=session_id,
        participant=participant,
        sample_rate=sr,
        channels=ch,
        language=language,
    )
    
    await transcription.start_transcription(
        session_id=session_id,
        language=language,
        sample_rate=sr,
        channels=ch,
    )
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                audio_data = message["bytes"]
                
                await session_manager.add_audio_chunk(session_id, audio_data)
                await transcription.send_audio(session_id, audio_data)
            
            elif "text" in message:
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type")
                    
                    if msg_type == "stop":
                        logger.info(f"Stop signal: {session_id}")
                        break
                    
                    elif msg_type == "reset":
                        logger.info(f"Reset signal: {session_id}")
                
                except json.JSONDecodeError:
                    pass
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    
    finally:
        await transcription.stop_transcription(session_id)
        await session_manager.end_session(session_id)