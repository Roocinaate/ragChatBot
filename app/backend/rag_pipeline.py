import os
from groq import Groq
from typing import List, Dict
import re

class RAGPipeline:
    def __init__(self, retriever, groq_api_key: str):
        self.retriever = retriever
        self.client = Groq(api_key=groq_api_key)
        print(f"✅ Groq client initialized with API key: {groq_api_key[:10]}...")
        
    def generate_chat_response(self, question: str, context_chunks: List[str], chat_history: List[Dict]) -> str:
        """Generate chat response using conversation history"""
        
        # Build context from retrieved chunks
        context = "\n\n".join([f"[Source {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks)])
        
        # Build conversation history for context
        history_text = ""
        for msg in chat_history[-6:]:  # Last 6 messages for context
            role = "User" if msg.role == "user" else "Assistant"
            history_text += f"{role}: {msg.content}\n"
        
        prompt = f"""You are HR Assistant, a helpful HR chatbot for Rikalp Capital Private Limited. You provide accurate information based on the company's HR policies.

CONVERSATION HISTORY:
{history_text}

HR POLICY CONTEXT:
{context}

CURRENT USER QUESTION: {question}

INSTRUCTIONS:
1. Provide accurate, conversational answers based ONLY on the HR policy context
2. Maintain a friendly, professional, and helpful tone
3. If the context doesn't contain relevant information, say: "I don't have specific information about this in the HR policy document, but I'd be happy to help with other HR-related questions!"
4. Reference previous conversation context when relevant
5. Keep responses concise but thorough
6. Use natural, conversational language

HR ASSISTANT:"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are HR Assistant, a friendly and professional HR chatbot. You provide accurate information based on company HR policies and maintain helpful conversations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,  # Slightly higher for more natural conversation
                max_tokens=1024,
                top_p=0.9
            )
            
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"I apologize, but I'm having trouble generating a response right now. Error: {str(e)}"
    
    def chat(self, question: str, chat_history: List[Dict], k: int = 3) -> Dict:
        """Chat method with conversation history"""
        print(f"🔍 Searching for relevant information for: '{question}'")
        
        # Retrieve relevant chunks
        retrieved_chunks = self.retriever.search(question, k=k)
        
        if not retrieved_chunks:
            return {
                "answer": "I couldn't find specific information about this in the HR policy document. Is there something else about HR policies I can help you with?",
                "sources": [],
                "scores": []
            }
        
        chunks_text = [chunk for chunk, score in retrieved_chunks]
        scores = [score for chunk, score in retrieved_chunks]
        
        print(f"📚 Found {len(chunks_text)} relevant chunks")
        
        # Generate chat response with history
        answer = self.generate_chat_response(question, chunks_text, chat_history)
        
        return {
            "answer": answer,
            "sources": chunks_text,
            "scores": scores
        }
    
    def query(self, question: str, k: int = 3) -> Dict:
        """Simple query method (backward compatibility)"""
        return self.chat(question, [], k)