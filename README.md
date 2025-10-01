# 🤖 HR Policy RAG Chatbot

A Retrieval-Augmented Generation (RAG) based chatbot that provides instant answers to HR policy questions using company documents. Built with FastAPI, Streamlit, FAISS, and Groq LLM.

## 🚀 Features

- **Document Intelligence**: Processes HR policy PDFs and creates intelligent embeddings
- **Instant Q&A**: Provides accurate answers based on company HR policies
- **Conversational Memory**: Remembers chat history and context
- **Source Citation**: Shows which policy sections were used for answers
- **Beautiful UI**: Modern, responsive chat interface
- **Fast Responses**: Powered by Groq's ultra-fast LLM inference

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **Vector Database**: FAISS
- **Embeddings**: Sentence Transformers
- **LLM**: Groq (Llama 3)
- **Document Processing**: PyPDF2, Text Chunking
- **Caching**: Redis (optional)

## 📁 Project Structure
    ```bash
   Rubix-RAG-Chatbot/
   ├── app/
   │ ├── backend/
   │ │ ├── api.py # FastAPI backend
   │ │ └── rag_pipeline.py # RAG pipeline logic
   │ ├── frontend/
   │ │ └── chat_ui.py # Streamlit frontend
   │ ├── ingestion/
   │ │ ├── pdf_processor.py # PDF text extraction
   │ │ └── chunking.py # Text chunking logic
   │ └── retrieval/
   │ ├── embeddings.py # Embedding generation
   │ └── faiss_index.py # Vector search with FAISS
   ├── models/
   │ └── embeddings.pkl # Pre-processed embeddings
   ├── data/
   │ └── raw/ # Raw documents
   ├── requirements.txt
   ├── process_document.py # Document processing script
   ├── .env # Environment variables
   └── README.md


## ⚡ Quick Start

### Prerequisites

- Python 3.8+
- Groq API key ([Get it here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Rubix-RAG-Chatbot

2. **Create virtual environment**
    ```bash
    python -m venv myenv

3. **Windows**
    ```bash
    myenv\Scripts\activate

4. **Mac/Linux**
    ```bash
    source myenv/bin/activate

5. **Install dependencies**
    ```bash
    pip install -r requirements.txt

6. **Create .env file**
    ```bash
    echo "GROQ_API_KEY=your_groq_api_key_here" > .env

🚀 Running the Application

Process the HR document (First time only)
    ```bash
    python process_document.py

Start the backend server (Terminal 1)
    ```bash
    uvicorn app.backend.api:app --reload --host 0.0.0.0 --port 8000

Start the frontend (Terminal 2)
    ```bash
    streamlit run app.frontend.chat_ui.py

Access the application

Frontend: http://localhost:8501

Backend API: http://localhost:8000

API Docs: http://localhost:8000/docs
