import streamlit as st
import json
from datetime import datetime
from utils.chromadb_manager import ChromaDBManager

class PerformanceDashboard:
    def __init__(self):
        self.chromadb_manager = ChromaDBManager()
    
    def render(self):
        st.header("🏆 Performance Dashboard")
        
        if not st.session_state.current_subject:
            st.info("Please select a subject and chapter from the sidebar to view your performance.")
            return
        
        # Overview metrics
        self.render_overview()
        
        # Subject-wise performance
        st.markdown("---")
        self.render_subject_performance()
        
        # Quiz performance details
        st.markdown("---")
        self.render_quiz_performance()
        
        # Learning analytics
        st.markdown("---")
        self.render_learning_analytics()
    
    def render_overview(self):
        st.subheader("📊 Overall Progress")
        
        # Calculate overall stats
        total_physics_parts = self.chromadb_manager.get_total_parts("physics_chapter1")
        total_chemistry_parts = self.chromadb_manager.get_total_parts("chemistry_chapter1")
        total_parts = total_physics_parts + total_chemistry_parts
        
        completed_parts = len(st.session_state.completed_parts)
        
        # Calculate average score
        avg_score = 0
        if st.session_state.quiz_scores:
            scores = [score['percentage'] for score in st.session_state.quiz_scores.values()]
            avg_score = sum(scores) / len(scores) if scores else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Progress",
                f"{completed_parts}/{total_parts}",
                delta=f"{(completed_parts/total_parts*100):.1f}%" if total_parts > 0 else "0%"
            )
        
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        with col3:
            st.metric("Badges Earned", len(st.session_state.badges))
        
        with col4:
            quiz_attempts = len(st.session_state.quiz_scores)
            st.metric("Quiz Attempts", quiz_attempts)
        
        # Progress bar
        if total_parts > 0:
            progress = completed_parts / total_parts
            st.progress(progress)
            st.caption(f"Overall completion: {progress*100:.1f}%")
    
    def render_subject_performance(self):
        st.subheader("📚 Subject-wise Performance")
        
        subjects = ["Physics", "Chemistry"]
        
        for subject in subjects:
            with st.expander(f"{subject} Chapter 1 Performance"):
                subject_key = subject.lower()
                
                # Get subject-specific stats
                total_parts = self.chromadb_manager.get_total_parts(f"{subject_key}_chapter1")
                subject_completed = [p for p in st.session_state.completed_parts 
                                   if p.startswith(f"{subject_key}_chapter1")]
                completed_count = len(subject_completed)
                
                # Subject metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if total_parts > 0:
                        completion_rate = (completed_count / total_parts) * 100
                        st.metric("Completion Rate", f"{completion_rate:.1f}%")
                    else:
                        st.metric("Completion Rate", "0%")
                
                # Subject-specific quiz scores
                subject_scores = {k: v for k, v in st.session_state.quiz_scores.items() 
                                if k.startswith(f"{subject_key}_chapter1")}
                
                with col2:
                    if subject_scores:
                        avg_subject_score = sum(s['percentage'] for s in subject_scores.values()) / len(subject_scores)
                        st.metric("Average Score", f"{avg_subject_score:.1f}%")
                    else:
                        st.metric("Average Score", "N/A")
                
                with col3:
                    subject_badges = [b for b in st.session_state.badges 
                                    if subject.lower() in b.lower()]
                    st.metric("Subject Badges", len(subject_badges))
                
                # Progress visualization
                if total_parts > 0:
                    st.progress(completed_count / total_parts)
                    st.caption(f"Parts completed: {completed_count}/{total_parts}")
                
                # Show recent quiz performance
                if subject_scores:
                    st.subheader("Recent Quiz Scores")
                    
                    for part_key, score_data in list(subject_scores.items())[-5:]:  # Last 5 attempts
                        part_num = part_key.split('_')[-1]
                        col_a, col_b, col_c = st.columns([2, 1, 1])
                        
                        with col_a:
                            st.text(f"Part {int(part_num) + 1}")
                        with col_b:
                            st.text(f"{score_data['score']}/{score_data['total']}")
                        with col_c:
                            color = "green" if score_data['passed'] else "red"
                            st.markdown(f"<span style='color: {color}'>{score_data['percentage']:.1f}%</span>", 
                                      unsafe_allow_html=True)
    
    def render_quiz_performance(self):
        st.subheader("🎯 Quiz Performance Analysis")
        
        if not st.session_state.quiz_scores:
            st.info("No quiz attempts yet. Complete some assessments to see your performance!")
            return
        
        # Performance trends
        quiz_data = []
        for key, score in st.session_state.quiz_scores.items():
            parts = key.split('_')
            subject = parts[0].title()
            part_num = int(parts[-1]) + 1
            
            quiz_data.append({
                'subject': subject,
                'part': part_num,
                'score': score['percentage'],
                'passed': score['passed'],
                'attempts': 1  # Could be enhanced to track multiple attempts
            })
        
        # Group by subject
        physics_scores = [d for d in quiz_data if d['subject'] == 'Physics']
        chemistry_scores = [d for d in quiz_data if d['subject'] == 'Chemistry']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Physics Scores")
            if physics_scores:
                for score_data in physics_scores:
                    status = "✅" if score_data['passed'] else "❌"
                    st.text(f"Part {score_data['part']}: {score_data['score']:.1f}% {status}")
            else:
                st.text("No Physics assessments completed")
        
        with col2:
            st.subheader("Chemistry Scores")
            if chemistry_scores:
                for score_data in chemistry_scores:
                    status = "✅" if score_data['passed'] else "❌"
                    st.text(f"Part {score_data['part']}: {score_data['score']:.1f}% {status}")
            else:
                st.text("No Chemistry assessments completed")
        
        # Performance insights
        st.subheader("📈 Performance Insights")
        
        all_scores = [d['score'] for d in quiz_data]
        if all_scores:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Highest Score", f"{max(all_scores):.1f}%")
            
            with col2:
                st.metric("Lowest Score", f"{min(all_scores):.1f}%")
            
            with col3:
                pass_rate = sum(1 for d in quiz_data if d['passed']) / len(quiz_data) * 100
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
        
        # Recommendations
        if all_scores:
            avg_score = sum(all_scores) / len(all_scores)
            
            if avg_score >= 85:
                st.success("🎉 Excellent performance! You're mastering the concepts well!")
            elif avg_score >= 75:
                st.info("👍 Good job! Keep up the consistent effort.")
            elif avg_score >= 60:
                st.warning("📚 Consider reviewing concepts more thoroughly before assessments.")
            else:
                st.error("💪 Don't give up! Try using the chat feature to clarify doubts.")
    
    def render_learning_analytics(self):
        st.subheader("📖 Learning Analytics")
        
        # Chat interaction stats
        chat_count = len(st.session_state.chat_history)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Questions Asked", chat_count)
        
        with col2:
            current_part = st.session_state.current_part
            st.metric("Current Learning Part", current_part + 1)
        
        # Recent learning activity
        if st.session_state.chat_history:
            st.subheader("Recent Questions")
            
            for i, chat in enumerate(st.session_state.chat_history[-3:]):
                with st.expander(f"Question {len(st.session_state.chat_history) - 2 + i}: {chat['question'][:30]}..."):
                    st.text(f"Selected Text: {chat['selected_text'][:50]}...")
                    st.text(f"Question: {chat['question']}")
                    st.text(f"Answer: {chat['answer'][:100]}...")
        
        # Study recommendations
        st.subheader("📋 Study Recommendations")
        
        # Analyze performance for recommendations
        if st.session_state.quiz_scores:
            failed_parts = []
            for key, score in st.session_state.quiz_scores.items():
                if not score['passed']:
                    parts = key.split('_')
                    subject = parts[0].title()
                    part_num = int(parts[-1]) + 1
                    failed_parts.append(f"{subject} Part {part_num}")
            
            if failed_parts:
                st.warning("Consider reviewing these parts:")
                for part in failed_parts:
                    st.text(f"• {part}")
            else:
                st.success("Great job! You're passing all assessments!")
        
        if chat_count == 0:
            st.info("💡 Tip: Use the text selection feature in the Learning page to ask questions and clarify concepts!")
        elif chat_count < 5:
            st.info("💡 Keep asking questions! The more you interact, the better you'll understand.")
        else:
            st.success("🎓 You're actively engaging with the content! Great learning approach!")
