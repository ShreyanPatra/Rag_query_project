import shutil
from pathlib import Path
from fastapi import FastAPI ,UploadFile,File,HTTPException,status
from fastapi.responses import StreamingResponse

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from app.config import settings
from app.rag import answer_query
from app.Vector_stores import vector_store_manager


app=FastAPI(
    title="Local Rag Engine",
    description="Backend API for Local Rag Engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question:str

class QueryResponse(BaseModel):
    question:str
    answer:str

class HealthResponse(BaseModel):
    status: str
    service: str


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int


@app.get("/")
def health_check():
    return HealthResponse(
        status="healthy",
        service=str(settings.APP_NAME)
    )

@app.post('/upload',status_code=status.HTTP_201_CREATED)
async def upload(file:UploadFile=File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,detail="Invalid File Format"
        )
    file_path=settings.DATA_DIR/file.filename
    try:
        with open(file_path,'wb') as buffer:
            shutil.copyfileobj(file.file,buffer)
    except Exception as e:
        raise HTTPException(status_code=500,detial=f"Failed to save file : {str(e)}")

    try:
        chunk_count=vector_store_manager.process_and_store_pdf(file_path)
        return UploadResponse(
            message="File processed and indexed successfully",
            filename=file.filename,
            chunks_created=chunk_count,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error indexing PDF: {str(e)}"
        )

@app.post("/stream-query")
async def stream_query(payload: QueryRequest):
    """Streams RAG generated response token-by-token."""
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        return StreamingResponse(
            answer_query(payload.question),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating streaming answer: {str(e)}"
        )