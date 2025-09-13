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
        if st.session_state.get(retry_key, False):
            st.info("📝 Here's a simplified version to help you understand better:")
            with st.spinner("Generating simplified content..."):
                simplified_content = self.orchestrator.simplify_content_for_retry(
                    st.session_state.current_subject,
                    st.session_state.current_part
                )
            st.markdown(simplified_content)
            # Reset retry flag
            st.session_state[retry_key] = False
        else:
            # Display original content
            st.markdown(content_data['content'])
        
        # Text selection for chat
        st.markdown("---")
        st.subheader("💬 Ask Questions About This Content")
        
        # Text selection input
        selected_text = st.text_area(
            "Select and paste text to ask questions about:",
            height=100,
            key="selected_text_input",
            placeholder="Copy and paste any part of the text above that you want to ask about..."
        )
        
        # Check for text input and trigger rerun if needed
        if selected_text and selected_text.strip():
            # Store selected text in session state for consistency
            if st.session_state.get("last_selected_text") != selected_text:
                st.session_state["last_selected_text"] = selected_text
                st.rerun()
        
        # Use session state text to ensure consistency
        display_text = st.session_state.get("last_selected_text", selected_text)
        
        if display_text and display_text.strip():
            # Suggested prompts
            st.subheader("Suggested Questions:")
            suggested_prompts = self.orchestrator.get_suggested_prompts()
            
            cols = st.columns(2)
            for i, prompt in enumerate(suggested_prompts):
                with cols[i % 2]:
                    if st.button(prompt, key=f"prompt_{i}"):
                        with st.spinner("Getting answer..."):
                            answer = self.orchestrator.handle_student_query(
                                st.session_state.current_subject,
                                display_text,
                                prompt
                            )
                        
                        # Add to chat history
                        chat_entry = {
                            'selected_text': display_text,
                            'question': prompt,
                            'answer': answer
                        }
                        st.session_state.chat_history.append(chat_entry)
                        st.rerun()
            
            # Custom question input
            custom_question = st.text_input(
                "Or ask your own question:",
                placeholder="Type your question here..."
            )
            
            if custom_question and st.button("Ask Question"):
                with st.spinner("Getting answer..."):
                    answer = self.orchestrator.handle_student_query(
                        st.session_state.current_subject,
                        display_text,
                        custom_question
                    )
                
                # Add to chat history
                chat_entry = {
                    'selected_text': display_text,
                    'question': custom_question,
                    'answer': answer
                }
                st.session_state.chat_history.append(chat_entry)
                st.rerun()
        
        # Display recent chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.subheader("Recent Q&A")
            
            # Show last 3 interactions
            for i, chat in enumerate(st.session_state.chat_history[-3:]):
                with st.expander(f"Q: {chat['question'][:50]}..."):
                    st.markdown(f"**Selected Text:** {chat['selected_text'][:100]}...")
                    st.markdown(f"**Question:** {chat['question']}")
                    st.markdown(f"**Answer:** {chat['answer']}")
        
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
                if st.button("✅ Mark as Complete & Take Assessment", type="primary"):
                    # Switch to assessment page
                    st.session_state.assessment_part = st.session_state.current_part
                    st.info("Please go to the Assessment page to take the quiz for this part.")
            else:
                st.success("This part is completed!")
                if st.button("🔄 Retake Assessment"):
                    st.session_state.assessment_part = st.session_state.current_part
                    st.info("Please go to the Assessment page to retake the quiz.")
        
        with col3:
            # Check if current part is completed before allowing next
            completion_key = f"{st.session_state.current_subject.lower()}_chapter1_part_{st.session_state.current_part}"
            if completion_key in st.session_state.completed_parts:
                if st.button("Next Part ➡️"):
                    st.session_state.current_part += 1
                    st.rerun()
            else:
                st.button("Next Part ➡️", disabled=True, help="Complete the assessment first")
