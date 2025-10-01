import streamlit as st
import requests
import json
import time
from datetime import datetime

# Configure the page - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="HR Policy Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful chat interface
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 0px 18px;
        margin: 8px 0;
        max-width: 70%;
        margin-left: auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .assistant-message {
        background: #f1f3f4;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 0px;
        margin: 8px 0;
        max-width: 70%;
        margin-right: auto;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Source badges */
    .source-badge {
        background: #e3f2fd;
        color: #1976d2;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin: 4px 4px 4px 0;
        display: inline-block;
    }
    
    /* Header - PERFECTLY CENTERED */
    .clean-header {
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 30px;
        background: transparent;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .main-heading {
        color: #2c3e50;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        text-align: center;
        width: 100%;
    }
    
    .sub-heading {
        color: #3498db;
        font-size: 1.4rem;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
        text-align: center;
        width: 100%;
    }
    
    /* Sample question buttons */
    .sample-question {
        width: 100%;
        margin: 5px 0;
        text-align: left;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: white;
        cursor: pointer;
    }
    .sample-question:hover {
        background: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

class HRChatbot:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
    
    def send_message(self, message: str, chat_history: list):
        """Send message to chat endpoint"""
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "message": message,
                    "conversation_id": st.session_state.get('conversation_id'),
                    "chat_history": chat_history
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code} - {response.text}"}
        except requests.exceptions.ConnectionError:
            return {"error": "❌ Cannot connect to backend API. Please make sure the server is running on port 8000."}
        except Exception as e:
            return {"error": f"❌ Error: {str(e)}"}

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    
    if "auto_question" not in st.session_state:
        st.session_state.auto_question = ""
    
    # Add welcome message if no messages exist
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hello! I'm your HR Assistant. I can help you with questions about company policies, leaves, benefits, code of conduct, and more! How can I assist you today?",
            "timestamp": datetime.now().isoformat()
        })

def display_chat_message(role, content, sources=None):
    """Display a chat message with proper styling"""
    if role == "user":
        st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{content}</div>', unsafe_allow_html=True)
        
        # Display sources if available
        if sources:
            with st.expander("📚 View Policy Sources", expanded=False):
                for i, source in enumerate(sources):
                    # Clean up the source text
                    clean_source = source.replace('===== Page', '📄 Page').replace('=====', '').strip()
                    st.markdown(f"**Source {i+1}:**")
                    st.markdown(f"```\n{clean_source[:400]}...\n```" if len(clean_source) > 400 else f"```\n{clean_source}\n```")
                    st.markdown("---")

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="clean-header">
        <h1 class="main-heading">🤖 HR Policy Chat Assistant</h1>
        <p class="sub-heading">Get instant answers about company policies, leaves, benefits, and HR rules</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot
    chatbot = HRChatbot()
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1001/1001371.png", width=80)
        st.title("HR Assistant")
        
        st.markdown("---")
        
        # New conversation button
        if st.button("🔄 Start New Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.session_state.auto_question = ""
            st.rerun()
        
        st.markdown("---")
        st.subheader("💡 Sample Questions")
        
        sample_questions = [
            "What is the maternity leave policy?",
            "How many earned leaves do employees get per year?",
            "What are the working hours and days?",
            "Tell me about the dress code policy",
            "How does the attendance system work?",
            "What is the probation period for new employees?",
            "Can you explain the leave policy?",
            "What is the sexual harassment policy?",
            "How are employee wages determined?",
            "What is the code of conduct?"
        ]
        
        for question in sample_questions:
            if st.button(f"• {question}", key=question):
                st.session_state.auto_question = question
                st.rerun()
        
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
        This AI assistant uses your company's HR policy document to provide accurate, instant answers.
        
        **Powered by:**
        - RAG (Retrieval Augmented Generation)
        - Groq AI for fast responses
        - FAISS for intelligent search
        """)
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                display_chat_message(
                    message["role"], 
                    message["content"],
                    message.get("sources")
                )
    
    # Handle auto-question from sidebar
    if st.session_state.auto_question:
        prompt = st.session_state.auto_question
        st.session_state.auto_question = ""  # Clear after use
    else:
        # Regular chat input
        prompt = st.chat_input("Type your HR question here...")
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            display_chat_message("user", prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("💭 Thinking...")
            
            # Prepare chat history for API (exclude current message)
            api_chat_history = []
            for msg in st.session_state.messages[:-1]:  # All except the last (current) message
                api_chat_history.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp")
                })
            
            # Get response from API
            response = chatbot.send_message(prompt, api_chat_history)
            
            if "error" in response:
                error_message = f"❌ {response['error']}"
                message_placeholder.markdown(error_message)
                full_response = error_message
                sources = []
            else:
                full_response = response["response"]
                sources = response.get("sources", [])
                
                # Simulate streaming response
                displayed_response = ""
                message_placeholder.markdown("🔄 Processing...")
                
                # Typewriter effect
                for char in full_response:
                    displayed_response += char
                    message_placeholder.markdown(displayed_response + "▌")
                    time.sleep(0.01)  # Adjust speed as needed
                
                message_placeholder.markdown(displayed_response)
                
                # Update conversation ID
                st.session_state.conversation_id = response.get("conversation_id")
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "sources": sources,
            "timestamp": datetime.now().isoformat()
        })
        
        # Auto-rerun to update the display
        st.rerun()

if __name__ == "__main__":
    main()