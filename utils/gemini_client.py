import streamlit as st
import os
import json
import re
from typing import Dict, List, Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Google GenAI library not available. Please install it.")
    st.stop()

class GeminiClient:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY not found in environment variables")
            st.stop()
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
    
    def generate_quiz_questions(self, content: str) -> Optional[List[Dict]]:
        """Generate 3-4 MCQ questions from content"""
        try:
            prompt = f"""
            Based on the following educational content, create exactly 4 multiple choice questions.
            
            Content: {content}
            
            Please format your response as a JSON array with this exact structure:
            [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Brief explanation of why this is correct"
                }}
            ]
            
            Requirements:
            - Questions should test understanding of key concepts
            - Options should be plausible but only one correct
            - correct_answer should be the index (0-3) of the correct option
            - Keep questions clear and concise
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response.text:
                questions = json.loads(response.text)
                return questions[:4]  # Ensure max 4 questions
            return None
            
        except Exception as e:
            st.error(f"Error generating quiz questions: {str(e)}")
            return None
    
    def simplify_content(self, content: str) -> str:
        """Simplify content for students who scored poorly"""
        try:
            prompt = f"""
            Simplify the following educational content for better understanding:
            
            Original content: {content}
            
            Please:
            1. Use simpler language and shorter sentences
            2. Add practical examples where possible
            3. Break down complex concepts into steps
            4. Use analogies to make concepts clearer
            5. Maintain all important information
            
            Return only the simplified content, no additional formatting.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text or content
            
        except Exception as e:
            st.error(f"Error simplifying content: {str(e)}")
            return content
    
    def answer_student_query(self, content: str, query: str) -> str:
        """Answer student query based on selected content"""
        try:
            prompt = f"""
            You are a helpful tutor. A student has selected this text from their textbook:
            
            Selected text: {content}
            
            Student's question: {query}
            
            Please provide a clear, helpful answer based on the selected content. 
            If the question asks for:
            - Explanation in Hinglish: Mix Hindi and English naturally
            - Examples: Provide relevant, easy-to-understand examples
            - Step-by-step explanation: Break it down clearly
            - Similar problems: Create practice problems if applicable
            
            Keep your answer educational but friendly and encouraging.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text or "Sorry, I couldn't process your question. Please try again."
            
        except Exception as e:
            st.error(f"Error answering query: {str(e)}")
            return "Sorry, there was an error processing your question."
    
    def generate_practice_problems(self, content: str) -> List[str]:
        """Generate practice problems based on content"""
        try:
            prompt = f"""
            Based on this educational content, create 2-3 practice problems or exercises:
            
            Content: {content}
            
            Return the problems as a simple list, one problem per line.
            Make them progressively challenging and relevant to the content.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response.text:
                problems = [p.strip() for p in response.text.split('\n') if p.strip()]
                return problems[:3]  # Max 3 problems
            return []
            
        except Exception as e:
            st.error(f"Error generating practice problems: {str(e)}")
            return []
