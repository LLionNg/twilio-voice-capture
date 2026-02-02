import asyncio
import json
from typing import Dict

import aiohttp
from loguru import logger

from app.core.config import get_settings


class TranscriptionService:
    
    def __init__(self):
        self.settings = get_settings()
        self.active_connections: Dict[str, dict] = {}
    
    async def start_transcription(
        self,
        session_id: str,
        language: str = "th-TH",
        sample_rate: int = 48000,
        channels: int = 1,
    ) -> None:
        session = aiohttp.ClientSession()
        
        params = f"?language={language}&sr={sample_rate}&ch={channels}"
        url = f"{self.settings.transcription_url}{params}"
        
        try:
            ws = await session.ws_connect(url)
            
            self.active_connections[session_id] = {
                "ws": ws,
                "session": session,
            }
            
            logger.info(f"Transcription started: {session_id}")
            
            asyncio.create_task(self._handle_responses(session_id, ws))
        
        except Exception as e:
            logger.error(f"Failed to start transcription: {e}")
            await session.close()
    
    async def send_audio(self, session_id: str, pcm_data: bytes) -> None:
        conn = self.active_connections.get(session_id)
        
        if conn:
            ws = conn["ws"]
            try:
                await ws.send_bytes(pcm_data)
            except Exception as e:
                logger.error(f"Failed to send audio: {e}")
    
    async def stop_transcription(self, session_id: str) -> None:
        conn = self.active_connections.pop(session_id, None)
        
        if conn:
            ws = conn["ws"]
            session = conn["session"]
            
            try:
                await ws.send_json({"type": "stop"})
                await ws.close()
            except:
                pass
            
            await session.close()
            logger.info(f"Transcription stopped: {session_id}")
    
    async def _handle_responses(
        self,
        session_id: str,
        ws: aiohttp.ClientWebSocketResponse,
    ) -> None:
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    logger.debug(f"Transcription response: {data.get('type')}")
                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"Transcription error: {ws.exception()}")
                    break
        
        except Exception as e:
            logger.error(f"Response handler error: {e}")
        
        finally:
            await self.stop_transcription(session_id)