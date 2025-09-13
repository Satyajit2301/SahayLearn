import streamlit as st
try:
    import PyPDF2
except ImportError:
    st.error("PyPDF2 not available. Please install it.")
    st.stop()

import re
from typing import List, Dict

class PDFProcessor:
    def __init__(self):
        self.chunk_size = 1000  # Characters per chunk
        
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from uploaded PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return self.clean_text(text)
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, chapter_title: str) -> List[Dict]:
        """Split text into learning chunks"""
        # Split into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    'id': f"chunk_{chunk_id}",
                    'content': current_chunk.strip(),
                    'chapter': chapter_title,
                    'part_number': chunk_id
                })
                current_chunk = sentence
                chunk_id += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                'id': f"chunk_{chunk_id}",
                'content': current_chunk.strip(),
                'chapter': chapter_title,
                'part_number': chunk_id
            })
        
        return chunks
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract major sections from text"""
        sections = {}
        # Simple section detection based on headers
        lines = text.split('\n')
        current_section = "Introduction"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers (capitalized lines or numbered sections)
            if (line.isupper() and len(line) > 5) or re.match(r'^\d+\.\d+', line):
                if current_content:
                    sections[current_section] = ' '.join(current_content)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = ' '.join(current_content)
        
        return sections
