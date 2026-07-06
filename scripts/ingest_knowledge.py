import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to Python path to allow app imports
sys.path.append(str(Path(__file__).parent.parent))

from app.rag.service import RagService
from app.config import get_settings

settings = get_settings()

async def main():
    rag_service = RagService()
    knowledge_dir = Path("uploaded_files/knowledge")
    
    if not knowledge_dir.exists():
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {knowledge_dir}")
        print("Please place your PDF system design books in this directory and run again.")
        return

    pdf_files = list(knowledge_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {knowledge_dir}.")
        return
        
    print(f"Found {len(pdf_files)} PDFs. Starting ingestion...")
    
    total_chunks = 0
    for pdf in pdf_files:
        print(f"Processing {pdf.name}...")
        try:
            # We index it as 'pattern' or 'general' doc type
            chunks = await rag_service.index_knowledge_document(str(pdf), doc_type="knowledge_book")
            total_chunks += chunks
            print(f"Successfully indexed {chunks} chunks for {pdf.name}")
        except Exception as e:
            print(f"Failed to process {pdf.name}: {str(e)}")
            
    print(f"Ingestion complete! Total new chunks added to vector store: {total_chunks}")

if __name__ == "__main__":
    asyncio.run(main())
