import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from utils.pdf_processor import PDFProcessor
from utils.chromadb_manager import ChromaDBManager
from components.learning_interface import LearningInterface
from components.assessment_interface import AssessmentInterface
from components.performance_dashboard import PerformanceDashboard
from components.badge_system import BadgeSystem

# Configure page
st.set_page_config(
    page_title="Sahay - Gamified Learning Platform",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.current_subject = None
    st.session_state.current_chapter = None
    st.session_state.current_part = 0
    st.session_state.completed_parts = []
    st.session_state.quiz_scores = {}
    st.session_state.badges = []
    st.session_state.selected_text = ""
    st.session_state.chat_history = []

def initialize_app():
    """Initialize the application by processing PDFs and setting up ChromaDB"""
    if not st.session_state.initialized:
        with st.spinner("Setting up learning platform..."):
            # Initialize ChromaDB
            chromadb_manager = ChromaDBManager()
            
            # Process and store PDFs if not already done
            pdf_processor = PDFProcessor()
            
            # Check if data is already loaded
            if not chromadb_manager.collection_exists("physics_chapter1"):
                st.info("Processing Physics Chapter 1...")
                physics_text = pdf_processor.extract_text_from_file("attached_assets/Class 12th Physics Chapter 1_1757775727919.pdf")
                physics_chunks = pdf_processor.chunk_text(physics_text, "Physics Chapter 1")
                chromadb_manager.store_chunks(physics_chunks, "physics_chapter1")
            
            if not chromadb_manager.collection_exists("chemistry_chapter1"):
                st.info("Processing Chemistry Chapter 1...")
                chemistry_text = pdf_processor.extract_text_from_file("attached_assets/Class 12th Chemistry Chapter 1_1757775727918.pdf")
                chemistry_chunks = pdf_processor.chunk_text(chemistry_text, "Chemistry Chapter 1")
                chromadb_manager.store_chunks(chemistry_chunks, "chemistry_chapter1")
            
            st.session_state.initialized = True
            st.success("Platform initialized successfully!")
            st.rerun()

def main():
    # Header
    st.title("🎓 Sahay - Gamified Learning Platform")
    st.markdown("*Learn Class 12th Physics and Chemistry with AI-powered assessments*")
    
    # Initialize app
    if not st.session_state.initialized:
        initialize_app()
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📖 Learning", "📊 Assessment", "🏆 Performance", "🎯 Badges"]
    )
    
    # Subject and Chapter Selection
    st.sidebar.markdown("---")
    st.sidebar.subheader("Select Content")
    
    subject = st.sidebar.selectbox(
        "Subject:",
        ["Physics", "Chemistry"]
    )
    
    chapter = st.sidebar.selectbox(
        "Chapter:",
        ["Chapter 1"]
    )
    
    if subject != st.session_state.current_subject or chapter != st.session_state.current_chapter:
        st.session_state.current_subject = subject
        st.session_state.current_chapter = chapter
        st.session_state.current_part = 0
        st.rerun()
    
    # Display current progress
    if st.session_state.current_subject:
        collection_name = f"{subject.lower()}_chapter1"
        chromadb_manager = ChromaDBManager()
        total_parts = chromadb_manager.get_total_parts(collection_name)
        completed = len([p for p in st.session_state.completed_parts if p.startswith(collection_name)])
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Progress")
        st.sidebar.progress(completed / max(total_parts, 1))
        st.sidebar.text(f"{completed}/{total_parts} parts completed")
    
    # Route to different pages
    if page == "📖 Learning":
        learning_interface = LearningInterface()
        learning_interface.render()
    elif page == "📊 Assessment":
        assessment_interface = AssessmentInterface()
        assessment_interface.render()
    elif page == "🏆 Performance":
        performance_dashboard = PerformanceDashboard()
        performance_dashboard.render()
    elif page == "🎯 Badges":
        badge_system = BadgeSystem()
        badge_system.render()

if __name__ == "__main__":
    main()
