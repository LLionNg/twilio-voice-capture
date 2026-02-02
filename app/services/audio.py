import audioop
import wave
from pathlib import Path

from loguru import logger


class AudioProcessor:
    
    @staticmethod
    def save_as_wav(
        audio_data: bytes,
        output_path: str | Path,
        sample_rate: int = 48000,
        channels: int = 1,
        sample_width: int = 2,
    ) -> None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
    
    @staticmethod
    def resample_pcm(
        pcm_data: bytes,
        from_rate: int,
        to_rate: int,
        channels: int = 1,
    ) -> bytes:
        if from_rate == to_rate:
            return pcm_data
        
        resampled, _ = audioop.ratecv(
            pcm_data,
            2,
            channels,
            from_rate,
            to_rate,
            None,
        )
        return resampled


class StreamBuffer:
    
    def __init__(self, sample_rate: int = 48000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer = bytearray()
    
    def add_chunk(self, chunk: bytes) -> None:
        self.buffer.extend(chunk)
    
    def get_buffer(self) -> bytes:
        return bytes(self.buffer)
    
    def clear(self) -> None:
        self.buffer.clear()
    
    def save_to_wav(self, output_path: str | Path) -> None:
        AudioProcessor.save_as_wav(
            self.get_buffer(),
            output_path,
            sample_rate=self.sample_rate,
            channels=self.channels,
            sample_width=2,
        )
        logger.info(f"Saved recording: {output_path}")