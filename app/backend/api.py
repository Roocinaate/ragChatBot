from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import pickle
import numpy as np
import sys
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title="HR RAG Chatbot API",
    version="1.0.0",
    description="A RAG-based HR Policy Chatbot API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str]
    chat_history: List[ChatMessage]

class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 3

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    scores: List[float]

# Global variables
rag_pipeline = None
conversation_store = {}

# Simple RAG Pipeline for testing
class MockRAGPipeline:
    def __init__(self):
        print("🤖 Mock RAG Pipeline initialized")
    
    def chat(self, question: str, chat_history: List[Dict]) -> Dict:
        return {
            "answer": f"This is a mock response to: '{question}'. The actual RAG system will process your HR policy questions.",
            "sources": ["HR Policy Document - Mock Source 1", "HR Policy Document - Mock Source 2"],
            "scores": [0.95, 0.87]
        }
    
    def query(self, question: str, k: int = 3) -> Dict:
        return self.chat(question, [])

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup"""
    global rag_pipeline
    print("🚀 Starting HR RAG Chatbot backend...")
    
    try:
        # Try to load pre-processed embeddings
        print("📁 Loading pre-processed embeddings...")
        with open('models/embeddings.pkl', 'rb') as f:
            data = pickle.load(f)
            embeddings = data['embeddings']
            chunks = data['chunks']
        
        print(f"📊 Loaded {len(chunks)} chunks with embeddings shape: {embeddings.shape}")
        
        # Import and initialize actual RAG components
        try:
            from app.retrieval.embeddings import EmbeddingGenerator
            from app.retrieval.faiss_index import FAISSRetriever
            from app.backend.rag_pipeline import RAGPipeline
            
            # Initialize retriever
            print("🔍 Building FAISS index...")
            embedder = EmbeddingGenerator()
            retriever = FAISSRetriever()
            retriever.model = embedder.model
            retriever.build_index(embeddings, chunks)
            
            # Initialize RAG pipeline
            print("🤖 Initializing RAG pipeline...")
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")
            
            rag_pipeline = RAGPipeline(retriever, groq_api_key)
            print("✅ Actual RAG pipeline initialized successfully!")
            
        except ImportError as e:
            print(f"⚠️  RAG components not available, using mock pipeline: {e}")
            rag_pipeline = MockRAGPipeline()
        except Exception as e:
            print(f"⚠️  Error initializing RAG pipeline, using mock: {e}")
            rag_pipeline = MockRAGPipeline()
        
    except FileNotFoundError:
        print("❌ Pre-processed embeddings not found. Using mock pipeline.")
        rag_pipeline = MockRAGPipeline()
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        print("💡 Using mock pipeline for now...")
        rag_pipeline = MockRAGPipeline()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🤖 HR RAG Chatbot API", 
        "status": "running",
        "rag_enabled": rag_pipeline is not None and not isinstance(rag_pipeline, MockRAGPipeline),
        "endpoints": {
            "root": "GET /",
            "health": "GET /health",
            "chat": "POST /chat",
            "query": "POST /query",
            "docs": "GET /docs"
        },
        "usage": "Visit /docs for interactive API documentation"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "HR RAG Chatbot API",
        "timestamp": datetime.now().isoformat(),
        "rag_enabled": rag_pipeline is not None and not isinstance(rag_pipeline, MockRAGPipeline)
    }

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint with conversation memory"""
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Generate or use conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get or initialize chat history
        if conversation_id not in conversation_store:
            conversation_store[conversation_id] = []
        
        current_history = conversation_store[conversation_id]
        
        # Add user message to history
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now().isoformat()
        )
        current_history.append(user_message)
        
        print(f"💬 Processing chat: '{request.message}'")
        
        # Generate response using RAG
        result = rag_pipeline.chat(request.message, current_history)
        
        # Add assistant response to history
        assistant_message = ChatMessage(
            role="assistant",
            content=result["answer"],
            timestamp=datetime.now().isoformat()
        )
        current_history.append(assistant_message)
        
        # Update conversation store
        conversation_store[conversation_id] = current_history
        
        return ChatResponse(
            response=result["answer"],
            conversation_id=conversation_id,
            sources=result["sources"],
            chat_history=current_history
        )
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

# Simple query endpoint (for backward compatibility)
@app.post("/query", response_model=QueryResponse)
async def query_hr_policy(request: QueryRequest):
    """Simple query endpoint"""
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        result = rag_pipeline.query(request.question, request.k)
        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            sources=result["sources"],
            scores=result.get("scores", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Test endpoint
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify the server is working"""
    return {
        "message": "✅ Server is working!",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": [
            "/",
            "/health", 
            "/test",
            "/docs",
            "/chat",
            "/query"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)