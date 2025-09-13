import streamlit as st
from typing import Optional

class BadgeSystem:
    def __init__(self):
        self.available_badges = {
            # Completion badges
            "first_steps": {
                "name": "First Steps",
                "description": "Completed your first part",
                "emoji": "👶",
                "condition": "complete_first_part"
            },
            "physics_explorer": {
                "name": "Physics Explorer",
                "description": "Completed 3 Physics parts",
                "emoji": "⚡",
                "condition": "physics_parts_3"
            },
            "chemistry_master": {
                "name": "Chemistry Master",
                "description": "Completed 3 Chemistry parts",
                "emoji": "🧪",
                "condition": "chemistry_parts_3"
            },
            "scholar": {
                "name": "Scholar",
                "description": "Completed 5 parts in total",
                "emoji": "🎓",
                "condition": "total_parts_5"
            },
            "perfectionist": {
                "name": "Perfectionist",
                "description": "Scored 100% on any quiz",
                "emoji": "💯",
                "condition": "perfect_score"
            },
            "consistent_learner": {
                "name": "Consistent Learner",
                "description": "Passed 5 assessments in a row",
                "emoji": "🔥",
                "condition": "streak_5"
            },
            "curious_mind": {
                "name": "Curious Mind",
                "description": "Asked 10 questions using chat",
                "emoji": "🤔",
                "condition": "questions_10"
            },
            "high_achiever": {
                "name": "High Achiever",
                "description": "Maintain 85%+ average score",
                "emoji": "🌟",
                "condition": "high_average"
            }
        }
    
    def render(self):
        st.header("🎯 Badge Collection")
        
        # Display earned badges
        st.subheader("🏆 Earned Badges")
        
        if st.session_state.badges:
            cols = st.columns(min(3, len(st.session_state.badges)))
            for i, badge_key in enumerate(st.session_state.badges):
                badge = self.available_badges.get(badge_key, {})
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; border: 2px solid gold; border-radius: 10px; margin: 10px;">
                        <div style="font-size: 48px;">{badge.get('emoji', '🏆')}</div>
                        <h4>{badge.get('name', 'Badge')}</h4>
                        <p>{badge.get('description', 'Achievement unlocked!')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No badges earned yet. Complete parts and take assessments to earn your first badge!")
        
        # Display available badges
        st.markdown("---")
        st.subheader("📋 Available Badges")
        
        cols = st.columns(2)
        for i, (key, badge) in enumerate(self.available_badges.items()):
            with cols[i % 2]:
                earned = key in st.session_state.badges
                
                if earned:
                    st.success(f"{badge['emoji']} {badge['name']} ✅")
                else:
                    st.info(f"{badge['emoji']} {badge['name']}")
                
                st.caption(badge['description'])
                
                # Show progress toward badge
                progress = self._get_badge_progress(key)
                if not earned and progress:
                    st.caption(f"Progress: {progress}")
        
        # Badge statistics
        st.markdown("---")
        st.subheader("📊 Badge Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Badges Earned", len(st.session_state.badges))
        
        with col2:
            st.metric("Total Available", len(self.available_badges))
        
        with col3:
            completion_rate = len(st.session_state.badges) / len(self.available_badges) * 100
            st.metric("Collection Rate", f"{completion_rate:.1f}%")
    
    def check_and_award_badges(self, subject: str, part_number: int, score: float) -> Optional[str]:
        """Check if any badges should be awarded and award them"""
        new_badges = []
        
        # Check each badge condition
        for badge_key, badge in self.available_badges.items():
            if badge_key not in st.session_state.badges:
                if self._check_badge_condition(badge['condition'], subject, part_number, score):
                    st.session_state.badges.append(badge_key)
                    new_badges.append(badge['name'])
        
        return new_badges[0] if new_badges else None
    
    def _check_badge_condition(self, condition: str, subject: str, part_number: int, score: float) -> bool:
        """Check if a specific badge condition is met"""
        
        if condition == "complete_first_part":
            return len(st.session_state.completed_parts) >= 1
        
        elif condition == "physics_parts_3":
            physics_parts = [p for p in st.session_state.completed_parts if p.startswith("physics_")]
            return len(physics_parts) >= 3
        
        elif condition == "chemistry_parts_3":
            chemistry_parts = [p for p in st.session_state.completed_parts if p.startswith("chemistry_")]
            return len(chemistry_parts) >= 3
        
        elif condition == "total_parts_5":
            return len(st.session_state.completed_parts) >= 5
        
        elif condition == "perfect_score":
            return score >= 100
        
        elif condition == "streak_5":
            # Check last 5 quiz scores for passing grades
            if len(st.session_state.quiz_scores) < 5:
                return False
            
            recent_scores = list(st.session_state.quiz_scores.values())[-5:]
            return all(s['passed'] for s in recent_scores)
        
        elif condition == "questions_10":
            return len(st.session_state.chat_history) >= 10
        
        elif condition == "high_average":
            if not st.session_state.quiz_scores:
                return False
            
            scores = [s['percentage'] for s in st.session_state.quiz_scores.values()]
            average = sum(scores) / len(scores)
            return average >= 85
        
        return False
    
    def _get_badge_progress(self, badge_key: str) -> Optional[str]:
        """Get progress string for a badge"""
        badge = self.available_badges.get(badge_key)
        if not badge:
            return None
        
        condition = badge['condition']
        
        if condition == "complete_first_part":
            completed = len(st.session_state.completed_parts)
            return f"{completed}/1 parts completed"
        
        elif condition == "physics_parts_3":
            physics_parts = [p for p in st.session_state.completed_parts if p.startswith("physics_")]
            return f"{len(physics_parts)}/3 Physics parts"
        
        elif condition == "chemistry_parts_3":
            chemistry_parts = [p for p in st.session_state.completed_parts if p.startswith("chemistry_")]
            return f"{len(chemistry_parts)}/3 Chemistry parts"
        
        elif condition == "total_parts_5":
            return f"{len(st.session_state.completed_parts)}/5 total parts"
        
        elif condition == "perfect_score":
            max_score = 0
            if st.session_state.quiz_scores:
                max_score = max(s['percentage'] for s in st.session_state.quiz_scores.values())
            return f"Highest score: {max_score:.1f}%"
        
        elif condition == "streak_5":
            if not st.session_state.quiz_scores:
                return "0/5 consecutive passes"
            
            # Count recent passing streak
            recent_scores = list(st.session_state.quiz_scores.values())
            streak = 0
            for score in reversed(recent_scores):
                if score['passed']:
                    streak += 1
                else:
                    break
            
            return f"{min(streak, 5)}/5 consecutive passes"
        
        elif condition == "questions_10":
            return f"{len(st.session_state.chat_history)}/10 questions asked"
        
        elif condition == "high_average":
            if not st.session_state.quiz_scores:
                return "Average: 0%"
            
            scores = [s['percentage'] for s in st.session_state.quiz_scores.values()]
            average = sum(scores) / len(scores)
            return f"Average: {average:.1f}% (need 85%+)"
        
        return None
    
    def show_badge_popup(self, badge_name: str):
        """Show a celebratory popup for earning a badge"""
        st.balloons()
        st.success(f"🎉 Congratulations! You earned the '{badge_name}' badge!")
