from pydantic import BaseSettings

class Settings(BaseSettings):
    channels :int
    rate:int 
    frames_per_buffer:int
    ping_interval:int
    ping_timeout:int
    openai_api_key:str

  
    class Config:
        env_file = "../.env"


settings = Settings()



