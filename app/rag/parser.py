# app/rag/parser.py
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def parse_pdf(file_path: str) -> List[str]:
    """Simple PDF parser - returns list of text chunks"""
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    
    chunks = text_splitter.split_documents(documents)
    return [chunk.page_content for chunk in chunks]