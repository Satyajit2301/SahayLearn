# Sahay - Gamified Learning Platform

## Overview

Sahay is a gamified learning platform designed for NCERT textbook study, specifically targeting Class 12th Physics and Chemistry. The platform provides an interactive learning experience where students read content in manageable parts, take assessments, and receive badges for achievements. Key features include progressive content unlocking based on assessment performance, contextual chat assistance with selected text, and simplified content generation for struggling students.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit-based web interface** with multi-page layout
- **Component-based structure** separating learning, assessment, performance tracking, and badge systems
- **Session state management** for tracking user progress, quiz scores, completed parts, and badges
- **Real-time content rendering** with dynamic part progression and assessment generation

### Backend Architecture
- **LangChain orchestration layer** managing data flow between vector database and LLM
- **PDF processing pipeline** for extracting and chunking NCERT textbook content
- **Text chunking strategy** splitting content into ~1000 character learning parts
- **Assessment generation system** creating MCQ questions from content chunks
- **Badge award system** tracking achievements and learning milestones

### Data Storage Solutions
- **ChromaDB vector database** for persistent storage of processed textbook chunks
- **Collection-based organization** (physics_chapter1, chemistry_chapter1)
- **Metadata storage** including chapter info, part numbers, and chunk IDs
- **Similarity search capabilities** for contextual chat responses and content retrieval

### Authentication and Authorization
- **Session-based state management** without persistent user accounts
- **Local storage approach** for current learning session tracking
- **No external authentication** implemented in current architecture

### Content Processing Pipeline
- **PDF text extraction** using PyPDF2 for NCERT textbook processing
- **Text cleaning and normalization** removing special characters and formatting
- **Intelligent chunking** based on sentence boundaries and size limits
- **Content simplification** for failed assessment retry scenarios

### Assessment and Gamification
- **Dynamic quiz generation** using LLM for content-specific questions
- **Performance tracking** with scoring, completion rates, and learning analytics
- **Badge system** with multiple achievement categories (completion, streak, perfection)
- **Adaptive content delivery** showing simplified versions for failed assessments

### Chat and Query System
- **Context-aware responses** using selected text and vector similarity search
- **Pre-loaded prompt suggestions** for common student questions
- **Multi-language support** including Hinglish explanations
- **Real-time query processing** with ChromaDB context retrieval

## External Dependencies

### Core APIs and Services
- **Google Gemini API** - Primary LLM for question generation, content simplification, and chat responses
- **ChromaDB** - Vector database for semantic search and content storage
- **Streamlit** - Web application framework and user interface

### Python Libraries
- **LangChain** - LLM orchestration and prompt management
- **PyPDF2** - PDF text extraction from NCERT textbooks
- **Google GenAI** - Gemini API client library

### Data Sources
- **NCERT PDF textbooks** - Class 12th Physics Chapter 1 and Chemistry Chapter 1
- **Local file storage** - PDF assets stored in attached_assets directory

### Infrastructure
- **Local ChromaDB persistence** - ./chroma_db directory for vector storage
- **Environment variables** - GEMINI_API_KEY for API authentication
- **Session state persistence** - Streamlit built-in session management