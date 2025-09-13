import streamlit as st
from utils.langchain_orchestrator import LangChainOrchestrator
from components.badge_system import BadgeSystem

class AssessmentInterface:
    def __init__(self):
        self.orchestrator = LangChainOrchestrator()
        self.badge_system = BadgeSystem()
    
    def render(self):
        st.header("📊 Assessment Center")
        
        if not st.session_state.current_subject:
            st.info("Please select a subject and chapter from the sidebar.")
            return
        
        # Check if there's a specific assessment to take
        assessment_part = st.session_state.get('assessment_part', st.session_state.current_part)
        
        st.subheader(f"Assessment for {st.session_state.current_subject} - Chapter 1, Part {assessment_part + 1}")
        
        # Generate or get questions
        if f"quiz_questions_{assessment_part}" not in st.session_state:
            with st.spinner("Generating quiz questions..."):
                questions = self.orchestrator.generate_assessment(
                    st.session_state.current_subject,
                    assessment_part
                )
                
                if questions:
                    st.session_state[f"quiz_questions_{assessment_part}"] = questions
                    st.session_state[f"user_answers_{assessment_part}"] = [None] * len(questions)
                else:
                    st.error("Unable to generate questions for this part.")
                    return
        
        questions = st.session_state[f"quiz_questions_{assessment_part}"]
        user_answers = st.session_state[f"user_answers_{assessment_part}"]
        
        # Display questions
        st.markdown("---")
        
        for i, question in enumerate(questions):
            st.subheader(f"Question {i + 1}")
            st.markdown(question['question'])
            
            # Radio button for options
            selected = st.radio(
                "Choose your answer:",
                options=range(len(question['options'])),
                format_func=lambda x: f"{chr(65 + x)}. {question['options'][x]}",
                key=f"q_{assessment_part}_{i}",
                index=user_answers[i] if user_answers[i] is not None else 0
            )
            
            # Update user answers
            st.session_state[f"user_answers_{assessment_part}"][i] = selected
            
            st.markdown("---")
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("Submit Assessment", type="primary"):
                # Validate answers
                result = self.orchestrator.validate_quiz_answers(
                    questions,
                    st.session_state[f"user_answers_{assessment_part}"]
                )
                
                # Store result
                quiz_key = f"{st.session_state.current_subject.lower()}_chapter1_part_{assessment_part}"
                st.session_state.quiz_scores[quiz_key] = result
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Assessment Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Score", f"{result['score']}/{result['total']}")
                with col2:
                    st.metric("Percentage", f"{result['percentage']:.1f}%")
                with col3:
                    if result['passed']:
                        st.success("✅ PASSED")
                    else:
                        st.error("❌ FAILED")
                
                # Feedback
                st.info(result['feedback'])
                
                # Handle pass/fail logic
                if result['passed']:
                    # Mark part as completed
                    completion_key = f"{st.session_state.current_subject.lower()}_chapter1_part_{assessment_part}"
                    if completion_key not in st.session_state.completed_parts:
                        st.session_state.completed_parts.append(completion_key)
                        
                        # Award badge
                        badge_earned = self.badge_system.check_and_award_badges(
                            st.session_state.current_subject,
                            assessment_part,
                            result['percentage']
                        )
                        
                        if badge_earned:
                            st.balloons()
                            st.success(f"🎉 Congratulations! You earned a new badge: {badge_earned}")
                    
                    # Show detailed results
                    with st.expander("📝 Detailed Results"):
                        for i, question in enumerate(questions):
                            user_answer = st.session_state[f"user_answers_{assessment_part}"][i]
                            correct = user_answer == question['correct_answer']
                            
                            st.markdown(f"**Question {i + 1}:** {question['question']}")
                            st.markdown(f"**Your Answer:** {chr(65 + user_answer)}. {question['options'][user_answer]}")
                            st.markdown(f"**Correct Answer:** {chr(65 + question['correct_answer'])}. {question['options'][question['correct_answer']]}")
                            
                            if correct:
                                st.success("✅ Correct!")
                            else:
                                st.error("❌ Incorrect")
                                st.info(f"**Explanation:** {question.get('explanation', 'No explanation available.')}")
                            
                            st.markdown("---")
                    
                    # Navigation
                    if st.button("Continue to Next Part 📖"):
                        if assessment_part == st.session_state.current_part:
                            st.session_state.current_part += 1
                        st.info("Go to the Learning page to continue with the next part.")
                
                else:
                    # Failed - offer simplified content
                    st.warning("Don't worry! You'll get another chance with simplified content.")
                    
                    # Set flag for simplified content
                    retry_key = f"retry_{st.session_state.current_subject.lower()}_part_{assessment_part}"
                    st.session_state[retry_key] = True
                    
                    # Show detailed results for learning
                    with st.expander("📝 Review Your Answers"):
                        for i, question in enumerate(questions):
                            user_answer = st.session_state[f"user_answers_{assessment_part}"][i]
                            correct = user_answer == question['correct_answer']
                            
                            st.markdown(f"**Question {i + 1}:** {question['question']}")
                            st.markdown(f"**Your Answer:** {chr(65 + user_answer)}. {question['options'][user_answer]}")
                            st.markdown(f"**Correct Answer:** {chr(65 + question['correct_answer'])}. {question['options'][question['correct_answer']]}")
                            
                            if not correct:
                                st.info(f"**Explanation:** {question.get('explanation', 'Review this concept in the learning material.')}")
                            
                            st.markdown("---")
                    
                    if st.button("Study Simplified Content 📚"):
                        st.info("Go to the Learning page to review the simplified version of this content.")
                
                # Clear assessment session state to allow retaking
                if st.button("🔄 Retake Assessment"):
                    del st.session_state[f"quiz_questions_{assessment_part}"]
                    del st.session_state[f"user_answers_{assessment_part}"]
                    st.rerun()
        
        # Show current progress
        st.markdown("---")
        st.subheader("📈 Your Progress")
        
        subject_key = st.session_state.current_subject.lower()
        completed_parts = [p for p in st.session_state.completed_parts if p.startswith(f"{subject_key}_chapter1")]
        
        if st.session_state.quiz_scores:
            scores = [score['percentage'] for key, score in st.session_state.quiz_scores.items() 
                     if key.startswith(f"{subject_key}_chapter1")]
            if scores:
                avg_score = sum(scores) / len(scores)
                st.metric("Average Score", f"{avg_score:.1f}%")
        
        st.info(f"Completed Parts: {len(completed_parts)}")
