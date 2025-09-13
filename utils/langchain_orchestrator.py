import streamlit as st
from typing import Dict, List, Optional
from .chromadb_manager import ChromaDBManager
from .gemini_client import GeminiClient

class LangChainOrchestrator:
    """Orchestrates data flow between ChromaDB and Gemini API"""
    
    def __init__(self):
        self.chromadb_manager = ChromaDBManager()
        self.gemini_client = GeminiClient()
    
    def get_learning_content(self, subject: str, part_number: int) -> Optional[Dict]:
        """Get content for a specific learning part"""
        collection_name = f"{subject.lower()}_chapter1"
        content = self.chromadb_manager.get_chunk_by_part(collection_name, part_number)
        
        if content:
            # Enhance content with metadata
            content['subject'] = subject
            content['part_number'] = part_number
            
        return content
    
    def generate_assessment(self, subject: str, part_number: int) -> Optional[List[Dict]]:
        """Generate assessment questions for a specific part"""
        # Get content from ChromaDB
        content_data = self.get_learning_content(subject, part_number)
        
        if not content_data:
            return None
        
        # Generate questions using Gemini
        questions = self.gemini_client.generate_quiz_questions(content_data['content'])
        
        return questions
    
    def handle_student_query(self, subject: str, selected_text: str, query: str) -> str:
        """Handle student chat queries with context from ChromaDB"""
        collection_name = f"{subject.lower()}_chapter1"
        
        # Find relevant content in ChromaDB
        relevant_content = self.chromadb_manager.get_content_by_text_selection(
            collection_name, selected_text
        )
        
        if relevant_content:
            context = relevant_content['content']
        else:
            # Fallback to similarity search
            similar_content = self.chromadb_manager.search_similar_content(
                collection_name, selected_text, n_results=1
            )
            context = similar_content[0]['content'] if similar_content else selected_text
        
        # Get answer from Gemini
        answer = self.gemini_client.answer_student_query(context, query)
        
        return answer
    
    def simplify_content_for_retry(self, subject: str, part_number: int) -> str:
        """Simplify content when student scores below 75%"""
        # Get original content
        content_data = self.get_learning_content(subject, part_number)
        
        if not content_data:
            return "Content not found."
        
        # Simplify using Gemini
        simplified = self.gemini_client.simplify_content(content_data['content'])
        
        return simplified
    
    def get_suggested_prompts(self, content_type: str = "general") -> List[str]:
        """Get suggested prompts for student queries"""
        prompts = {
            "general": [
                "Can you explain this in Hinglish?",
                "Can you give me an example?",
                "What is the main concept here?",
                "How is this used in real life?"
            ],
            "numerical": [
                "Can you explain step by step?",
                "Can you generate another similar problem?",
                "What formula should I use here?",
                "Can you break down this calculation?"
            ],
            "concept": [
                "Can you simplify this explanation?",
                "What are the key points to remember?",
                "How does this connect to other topics?",
                "Can you provide more examples?"
            ]
        }
        
        return prompts.get(content_type, prompts["general"])
    
    def search_content(self, subject: str, search_query: str) -> List[Dict]:
        """Search for content across the subject"""
        collection_name = f"{subject.lower()}_chapter1"
        results = self.chromadb_manager.search_similar_content(
            collection_name, search_query, n_results=5
        )
        
        return results
    
    def validate_quiz_answers(self, questions: List[Dict], user_answers: List[int]) -> Dict:
        """Validate quiz answers and calculate score"""
        if not questions or len(questions) != len(user_answers):
            return {"score": 0, "total": 0, "percentage": 0, "passed": False}
        
        correct_count = 0
        total_questions = len(questions)
        
        for i, question in enumerate(questions):
            if i < len(user_answers) and user_answers[i] == question['correct_answer']:
                correct_count += 1
        
        percentage = (correct_count / total_questions) * 100
        passed = percentage >= 75
        
        return {
            "score": correct_count,
            "total": total_questions,
            "percentage": percentage,
            "passed": passed,
            "feedback": self._generate_feedback(percentage)
        }
    
    def _generate_feedback(self, percentage: float) -> str:
        """Generate feedback based on score"""
        if percentage >= 90:
            return "Excellent work! You've mastered this concept. 🎉"
        elif percentage >= 75:
            return "Great job! You can move to the next part. 👍"
        elif percentage >= 50:
            return "Good effort! Review the material and try again. 📚"
        else:
            return "Don't worry! Let's go through the simplified version. 💪"
