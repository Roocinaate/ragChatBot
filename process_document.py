import os
import sys
import pickle
import numpy as np
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ingestion.pdf_processor import PDFProcessor
from app.ingestion.chunking import TextChunker
from app.retrieval.embeddings import EmbeddingGenerator

def process_hr_document():
    """Process the HR policy PDF and generate embeddings"""
    
    # Create necessary directories
    Path("models").mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)
    
    # Check if PDF exists
    pdf_path = "HR-Policy (1).pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file '{pdf_path}' not found!")
        print("Please make sure 'HR-Policy (1).pdf' is in the project root directory")
        return False
    
    print("📄 Step 1: Extracting text from PDF...")
    processor = PDFProcessor()
    text = processor.process_hr_policy(pdf_path)
    
    if not text:
        print("❌ Failed to extract text from PDF")
        return False
    
    print(f"📊 Extracted {len(text)} characters of text")
    
    print("✂️ Step 2: Chunking text...")
    chunker = TextChunker(chunk_size=512, chunk_overlap=50)
    chunks = chunker.chunk_text(text)
    
    print(f"📦 Created {len(chunks)} text chunks")
    
    print("🔤 Step 3: Generating embeddings...")
    embedder = EmbeddingGenerator()
    embeddings = embedder.generate_embeddings(chunks)
    
    print("💾 Step 4: Saving embeddings and chunks...")
    # Save embeddings and chunks together
    with open('models/embeddings.pkl', 'wb') as f:
        pickle.dump({
            'embeddings': embeddings,
            'chunks': chunks
        }, f)
    
    # Also save chunks as text for inspection
    with open('models/chunks.txt', 'w', encoding='utf-8') as f:
        for i, chunk in enumerate(chunks):
            f.write(f"=== Chunk {i+1} ===\n")
            f.write(chunk[:500] + "..." if len(chunk) > 500 else chunk)
            f.write(f"\n(Length: {len(chunk)} characters)\n")
            f.write("\n" + "="*50 + "\n\n")
    
    print("✅ Document processing completed successfully!")
    print(f"📁 Embeddings saved to: models/embeddings.pkl")
    print(f"📁 Text preview saved to: models/chunks.txt")
    print(f"📊 Embeddings shape: {embeddings.shape}")
    
    return True

if __name__ == "__main__":
    success = process_hr_document()
    if success:
        print("\n🎉 Document processing complete!")
        print("\n🚀 Now you can start the full RAG system:")
        print("1. Start the backend: uvicorn app.backend.api:app --reload --port 8000")
        print("2. Start the frontend: streamlit run app/frontend/chat_ui.py")
        print("3. Test with questions like: 'What is the maternity leave policy?' or 'How many leaves do employees get?'")
    else:
        sys.exit(1)