import os
import uvicorn
from app.backend.api import app as fastapi_app
from app.frontend.chat_ui import main as streamlit_app

def main():
    """Main entry point - run both FastAPI and Streamlit"""
    print("Starting HR RAG Chatbot...")
    print("FastAPI backend: http://localhost:8000")
    print("Streamlit frontend: http://localhost:8501")
    
    # In production, you'd run these separately
    # For development, this shows how to start both
    print("\nTo start backend: uvicorn app.backend.api:app --reload --port 8000")
    print("To start frontend: streamlit run app/frontend/chat_ui.py")

if __name__ == "__main__":
    main()