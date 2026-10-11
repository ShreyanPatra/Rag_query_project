import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_URL=Path(__file__).resolve().parent.parent
class Settings(BaseSettings):

    DATA_DIR:Path=BASE_URL/"PDF_FILE"
    CHROMA_PATH:Path=BASE_URL/"chroma_DB"

    Ollama_Base_url:str=os.getenv("Ollama_Base_Url","http://localhost:11434")

    LLM_Model:str='llama3:latest'
    Embedding_Model:str="nomic-embed-text:latest"
    APP_NAME:str="Local Rag Engine"


    class Config:
        env_file=".env"
        extra="ignore"

settings=Settings()

os.makedirs(settings.DATA_DIR,exist_ok=True)
os.makedirs(settings.CHROMA_PATH,exist_ok=True)

