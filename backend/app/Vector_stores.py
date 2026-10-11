from pathlib import Path
from typing import Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from langchain_core.documents import Document
from app.config import settings

class VectorStoreManager:
    def __init__(self):
        self.embeddings=OllamaEmbeddings(base_url=settings.Ollama_Base_url,model=settings.Embedding_Model,)

        self.chroma_path=str(settings.CHROMA_PATH)

    def get_vectorstore(self):
        return Chroma(
            persist_directory=self.chroma_path,
            embedding_function=self.embeddings)
    
    def process_and_store_pdf(self,file_path:Path):
        loader=PyPDFLoader(str(file_path))
        documents=loader.load()

        if not documents:
            raise ValueError("Provided Pdf could not be read.")

        text_splitter=RecursiveCharacterTextSplitter(chunk_size=600,
        chunk_overlap=120)

        chunks=text_splitter.split_documents(documents)

        vectorstore=self.get_vectorstore()
        vectorstore.add_documents(chunks)

        return len(chunks)
    def get_retriever(self,search_k:int=4):
        vectorstore=self.get_vectorstore()

        return vectorstore.as_retriever(
            search_type='similarity',
            search_kwargs={"k":search_k}
        )

vector_store_manager=VectorStoreManager()

