# app/rag/service.py
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import get_settings

settings = get_settings()

class RagService:
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._init_vectorstore()

    def _init_vectorstore(self):
        """Initialize Chroma vector store (updated)"""
        from langchain_chroma import Chroma
        import os
        
        persist_directory = settings.vectorstore_dir
        os.makedirs(persist_directory, exist_ok=True)
        
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=settings.chroma_collection_name
        )

    async def process_document(self, file_path: str) -> str:
        """Process uploaded PDF and return relevant context"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)

        # Add to vector store
        if chunks:
            self.vectorstore.add_documents(chunks)

        # Retrieve relevant context
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 6}
        )
        
        # For initial architecture generation, return concatenated relevant docs
        docs = retriever.invoke("Software architecture requirements and system design")
        context = "\n\n".join([doc.page_content for doc in docs])
        
        return context

    async def retrieve_context(self, query: str, k: int = 5) -> str:
        """General retrieval for any query"""
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])