import PyPDF2
import re
from typing import List, Dict

class PDFProcessor:
    def __init__(self):
        self.text_chunks = []
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += f"===== Page {page_num + 1} =====\n"
                text += page.extract_text() + "\n\n"
        return text
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        return text.strip()
    
    def process_hr_policy(self, pdf_path: str) -> str:
        """Main method to process HR policy PDF"""
        raw_text = self.extract_text_from_pdf(pdf_path)
        cleaned_text = self.clean_text(raw_text)
        return cleaned_text