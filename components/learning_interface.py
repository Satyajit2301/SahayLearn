import streamlit as st
from utils.langchain_orchestrator import LangChainOrchestrator
from components.badge_system import BadgeSystem

class LearningInterface:
    def __init__(self):
        self.orchestrator = LangChainOrchestrator()
        self.badge_system = BadgeSystem()
    
    def render(self):
        st.header("📖 Learning Interface")
        
        if not st.session_state.current_subject:
            st.info("Please select a subject and chapter from the sidebar to start learning.")
            return
        
        # Get current content
        content_data = self.orchestrator.get_learning_content(
            st.session_state.current_subject,
            st.session_state.current_part
        )
        
        if not content_data:
            st.error("No content found for the selected part.")
            return
        
        # Display current part info
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"{st.session_state.current_subject} - {st.session_state.current_chapter}")
        with col2:
            st.metric("Current Part", st.session_state.current_part + 1)
        with col3:
            completion_key = f"{st.session_state.current_subject.lower()}_chapter1_part_{st.session_state.current_part}"
            is_completed = completion_key in st.session_state.completed_parts
            st.success("✅ Completed" if is_completed else "📖 In Progress")
        
        # Display content
        st.markdown("---")
        
        # Check if this part was failed and needs simplified version
        retry_key = f"retry_{st.session_state.current_subject.lower()}_part_{st.session_state.current_part}"
        cache_key = f"simplified_cache_{st.session_state.current_subject.lower()}_part_{st.session_state.current_part}"
        
        if st.session_state.get(retry_key, False):
            col_simp_title, col_simp_btn = st.columns([3, 1])
            with col_simp_title:
                st.info("📝 **Simplified Version** (tailored to help you understand better):")
            with col_simp_btn:
                if st.button("📖 View Original Text", key="view_orig_btn"):
                    st.session_state[retry_key] = False
                    st.rerun()
            
            # Use cached version if already generated, otherwise generate and cache
            if cache_key in st.session_state:
                simplified_content = st.session_state[cache_key]
            else:
                with st.spinner("Generating simplified concept summary..."):
                    simplified_content = self.orchestrator.simplify_content_for_retry(
                        st.session_state.current_subject,
                        st.session_state.current_part
                    )
                    st.session_state[cache_key] = simplified_content
            
            st.markdown(simplified_content)
        else:
            col_orig_title, col_orig_btn = st.columns([3, 1])
            with col_orig_title:
                st.markdown(f"### Lesson Content (Part {st.session_state.current_part + 1})")
            with col_orig_btn:
                if cache_key in st.session_state:
                    if st.button("📝 View Simplified Version", key="view_simp_btn"):
                        st.session_state[retry_key] = True
                        st.rerun()
            st.markdown(content_data['content'])
        
        # 💬 AI Tutor Chat Section
        st.markdown("---")
        col_chat_title, col_chat_clear = st.columns([3, 1])
        with col_chat_title:
            st.subheader("💬 Ask Your AI Tutor")
        with col_chat_clear:
            if st.session_state.chat_history:
                if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
                    st.session_state.chat_history = []
                    st.rerun()
        
        # Quick suggested questions
        st.markdown("**💡 Quick Questions:**")
        suggested_prompts = self.orchestrator.get_suggested_prompts()
        cols = st.columns(len(suggested_prompts))
        quick_question_clicked = None
        for i, prompt in enumerate(suggested_prompts):
            with cols[i]:
                if st.button(prompt, key=f"quick_prompt_{i}", use_container_width=True):
                    quick_question_clicked = prompt
        
        # Display Chat History
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history and not quick_question_clicked:
                st.info("👋 Have a doubt? Type your question in the chat box below and press **Enter** to ask the AI Tutor!")
            else:
                for chat in st.session_state.chat_history:
                    with st.chat_message("user"):
                        st.markdown(chat['question'])
                    with st.chat_message("assistant", avatar="🎓"):
                        st.markdown(chat['answer'])
        
        # Unified Chat Input (Pressing Enter sends the question immediately)
        user_input = st.chat_input("Ask a question about this chapter... (Type and press Enter)")
        
        # Handle new question submission from either chat_input or a quick question button
        question_to_process = user_input or quick_question_clicked
        if question_to_process:
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(question_to_process)
                
                with st.chat_message("assistant", avatar="🎓"):
                    with st.spinner("AI Tutor is answering..."):
                        answer = self.orchestrator.handle_student_query(
                            st.session_state.current_subject,
                            content_data['content'],
                            question_to_process
                        )
                        st.markdown(answer)
            
            # Save to chat history
            st.session_state.chat_history.append({
                'selected_text': f"{st.session_state.current_subject} - Part {st.session_state.current_part + 1}",
                'question': question_to_process,
                'answer': answer
            })
            
            # Check badge for questions asked
            self.badge_system.check_and_award_badges(
                st.session_state.current_subject,
                st.session_state.current_part,
                0
            )
            st.rerun()
        
        # Navigation and completion buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_part > 0:
                if st.button("⬅️ Previous Part"):
                    st.session_state.current_part -= 1
                    st.rerun()
        
        with col2:
            completion_key = f"{st.session_state.current_subject.lower()}_chapter1_part_{st.session_state.current_part}"
            if completion_key not in st.session_state.completed_parts:
                if st.button("✅ Mark as Complete & Take Assessment", type="primary", use_container_width=True):
                    st.session_state.assessment_part = st.session_state.current_part
                    st.info("Please navigate to the 📊 Assessment page from the sidebar to take the quiz.")
            else:
                st.success("This part is completed!")
                if st.button("🔄 Retake Assessment", use_container_width=True):
                    st.session_state.assessment_part = st.session_state.current_part
                    st.info("Please navigate to the 📊 Assessment page to retake the quiz.")
        
        with col3:
            completion_key = f"{st.session_state.current_subject.lower()}_chapter1_part_{st.session_state.current_part}"
            if completion_key in st.session_state.completed_parts:
                if st.button("Next Part ➡️"):
                    st.session_state.current_part += 1
                    st.rerun()
            else:
                st.button("Next Part ➡️", disabled=True, help="Complete the assessment first")
