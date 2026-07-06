# app/rag/service.py
import os
import logging
from typing import Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from app.config import get_settings
from app.utils.logger import log_info, log_error

settings = get_settings()


class RagService:
    """
    Two-mode RAG service:

    1. Direct Injection (SRS / any PDF):
       Reads the *entire* PDF text and returns it as a plain string.
       Leverages Gemini's 1M-token context window instead of fragmenting
       the document into chunks that lose coherence.

    2. Knowledge-Base Retrieval (design patterns, compliance standards):
       Uses ChromaDB to store and retrieve architecture patterns, security
       standards and compliance docs. Used by SecurityAgent at query time.
    """

    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
        )
        self._init_knowledge_store()

    # ------------------------------------------------------------------
    # Initialise the persistent knowledge-base vector store
    # ------------------------------------------------------------------
    def _init_knowledge_store(self):
        persist_dir = settings.vectorstore_dir
        os.makedirs(persist_dir, exist_ok=True)
        self.knowledge_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=settings.chroma_collection_name,
        )
        log_info("Knowledge-base vector store initialised at %s", persist_dir)

    # ------------------------------------------------------------------
    # MODE 1 — Direct full-document injection (no chunking)
    # ------------------------------------------------------------------
    async def extract_full_text(self, file_path: str) -> str:
        """
        Extract *all* text from a PDF and return it as a single string.
        No chunking, no vector store — plain text for direct LLM injection.
        Ideal for SRS / design docs where the LLM should see everything.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        loader = PyPDFLoader(file_path)
        pages = loader.load()
        full_text = "\n\n".join(
            f"[Page {i + 1}]\n{page.page_content}" for i, page in enumerate(pages)
        )
        log_info(
            "Extracted %d pages / %d chars from %s",
            len(pages), len(full_text), Path(file_path).name,
        )
        return full_text

    # kept for backward compatibility
    async def process_document(self, file_path: str) -> str:
        return await self.extract_full_text(file_path)

    async def index_srs_document(self, file_path: str, session_id: str) -> int:
        """
        Chunk and index a user's SRS document into the knowledge base,
        tagged specifically with their session_id so agents can retrieve chunks.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        loader = PyPDFLoader(file_path)
        pages = loader.load()
        chunks = self.text_splitter.split_documents(pages)

        for chunk in chunks:
            chunk.metadata["doc_type"] = "srs_document"
            chunk.metadata["session_id"] = session_id
            chunk.metadata["source_file"] = Path(file_path).name

        self.knowledge_store.add_documents(chunks)
        log_info("Indexed %d chunks (srs_document) for session %s", len(chunks), session_id)
        return len(chunks)

    async def retrieve_srs_context(self, query: str, session_id: str, k: int = 5) -> str:
        """
        Retrieve relevant chunks from a specific user's indexed SRS document.
        """
        retriever = self.knowledge_store.as_retriever(
            search_kwargs={
                "k": k,
                "filter": {
                    "$and": [
                        {"doc_type": "srs_document"},
                        {"session_id": session_id}
                    ]
                }
            }
        )
        docs = retriever.invoke(query)

        if not docs:
            return ""

        return "\n\n---\n\n".join(
            f"[Source: {d.metadata.get('source_file', 'srs-document')}]\n{d.page_content}"
            for d in docs
        )

    # ------------------------------------------------------------------
    # MODE 2 — Knowledge-base operations (chunked, persisted)
    # ------------------------------------------------------------------
    async def index_knowledge_document(self, file_path: str, doc_type: str = "general") -> int:
        """
        Chunk and index a document into the persistent knowledge base.
        Use for design patterns, compliance PDFs, ADRs, security standards —
        documents you want to query *across* many projects.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        loader = PyPDFLoader(file_path)
        pages = loader.load()
        chunks = self.text_splitter.split_documents(pages)

        for chunk in chunks:
            chunk.metadata["doc_type"] = doc_type
            chunk.metadata["source_file"] = Path(file_path).name

        self.knowledge_store.add_documents(chunks)
        log_info("Indexed %d chunks (%s) from %s", len(chunks), doc_type, Path(file_path).name)
        return len(chunks)

    async def index_text(self, text: str, metadata: dict = None) -> int:
        """
        Directly index a plain-text snippet (e.g. web search results)
        into the knowledge base so future queries skip the web entirely.
        """
        from langchain_core.documents import Document

        chunks = self.text_splitter.split_text(text)
        docs = [Document(page_content=chunk, metadata=metadata or {}) for chunk in chunks]
        self.knowledge_store.add_documents(docs)
        log_info("Indexed %d text chunks into knowledge base", len(docs))
        return len(docs)

    async def retrieve(self, query: str, k: int = 6, doc_type: Optional[str] = None) -> str:
        """
        Retrieve relevant chunks from the knowledge base.
        Optionally filter by doc_type ('security', 'pattern', 'compliance').
        Returns a concatenated string ready to be injected into a prompt.
        """
        retriever_kwargs: dict = {"k": k}
        if doc_type:
            retriever_kwargs["filter"] = {"doc_type": doc_type}

        retriever = self.knowledge_store.as_retriever(search_kwargs=retriever_kwargs)
        docs = retriever.invoke(query)

        if not docs:
            return ""

        return "\n\n---\n\n".join(
            f"[Source: {d.metadata.get('source_file', 'knowledge-base')}]\n{d.page_content}"
            for d in docs
        )

    # kept for backward compat
    async def retrieve_context(self, query: str, k: int = 5) -> str:
        return await self.retrieve(query, k=k)