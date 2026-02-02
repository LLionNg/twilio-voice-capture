from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8082
    
    sample_rate: int = 48000
    audio_channels: int = 1
    language: str = "th-TH"
    
    output_dir: str = "output"
    
    transcription_url: str = "wss://aivcs-api-ai-production.up.railway.app/ws/transcribe?language=th-TH&sr=48000&ch=1"
    
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    @property
    def use_s3(self) -> bool:
        return bool(
            self.aws_bucket_name 
            and self.aws_access_key_id 
            and self.aws_secret_access_key
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()