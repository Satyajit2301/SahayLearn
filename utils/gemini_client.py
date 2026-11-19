import streamlit as st
import os
import json
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Google GenAI library not available. Please install it.")
    st.stop()

class GeminiClient:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            
        if not api_key:
            st.error("GEMINI_API_KEY not found in environment variables or .env file.")
            st.stop()
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.5-flash-lite"
        self.fallback_models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.7-flash",
            "gemini-3.8-flash"
        ]

    def _generate_with_fallback(self, contents: str, config: Optional[types.GenerateContentConfig] = None):
        """Generate content with automatic fallback across available Gemini models."""
        seen = set()
        models = [m for m in [self.model] + self.fallback_models if not (m in seen or seen.add(m))]
        
        last_exception = None
        for model_name in models:
            try:
                if config:
                    return self.client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config
                    )
                else:
                    return self.client.models.generate_content(
                        model=model_name,
                        contents=contents
                    )
            except Exception as e:
                last_exception = e
                continue
        
        if last_exception:
            raise last_exception
    
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
            
            response = self._generate_with_fallback(
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if response and response.text:
                text = response.text.strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                questions = json.loads(text)
                return questions[:4]  # Ensure max 4 questions
            return None
            
        except Exception as e:
            st.error(f"Error generating quiz questions: {str(e)}")
            return None
    
    def simplify_content(self, content: str) -> str:
        """Simplify content for students who scored poorly"""
        try:
            text_to_simplify = content[:1500] if len(content) > 1500 else content
            prompt = f"""
You are an expert tutor explaining this to a student who struggled with a quiz on this topic.
Simplify the following textbook section into clear, easy-to-understand points:

Text:
{text_to_simplify}

Provide:
1. 💡 **Core Idea** (1-2 simple sentences)
2. 🔑 **Key Points to Remember** (3-4 concise bullet points)
3. 🍎 **Real-life Analogy** (1 short, relatable example)

Keep it concise, clear, and direct. No conversational preamble.
"""
            
            response = self._generate_with_fallback(contents=prompt)
            return (response.text if response else None) or content
            
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
            
            response = self._generate_with_fallback(contents=prompt)
            return (response.text if response else None) or "Sorry, I couldn't process your question. Please try again."
            
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
            
            response = self._generate_with_fallback(contents=prompt)
            if response and response.text:
                problems = [p.strip() for p in response.text.split('\n') if p.strip()]
                return problems[:3]  # Max 3 problems
            return []
            
        except Exception as e:
            st.error(f"Error generating practice problems: {str(e)}")
            return []
