from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    provider : str = "dummy"

    hf_model_id : str | None = None
    hf_token : str | None = None

    service_name : str = "llm-harmonizer"
    service_version : str = "0.2.0"

    class Config:
        env_file = ".env"

settings =  Settings()