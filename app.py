# app.py
"""
ECHO - Personal AI Memory System
Streamlit UI for interacting with your AI memory system
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from modules import EventLogger, TemporalEngine, MemoryEngine, AIReflection, QueryInterface

# Page configuration
st.set_page_config(
    page_title="ECHO - Personal AI Memory",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for playful but clean design
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        background: rgba(255,255,255,0.95);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .insight-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 0.5rem;
        border-radius: 10px;
        margin: 0.25rem 0;
    }
    .user-message {
        background: #e3f2fd;
        text-align: right;
    }
    .echo-message {
        background: #f5f5f5;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.event_logger = EventLogger()
    st.session_state.temporal_engine = TemporalEngine(st.session_state.event_logger)
    st.session_state.memory_engine = MemoryEngine(
        st.session_state.event_logger, 
        st.session_state.temporal_engine
    )
    st.session_state.ai_reflection = AIReflection(st.session_state.memory_engine)
    st.session_state.query_interface = QueryInterface(
        st.session_state.event_logger,
        st.session_state.memory_engine,
        st.session_state.ai_reflection
    )
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/brain_1f9e0.png", width=80)
    st.title("🧠 ECHO")
    st.markdown("*Your Personal AI Memory System*")
    st.markdown("---")
    
    # Quick stats
    st.subheader("📊 Quick Stats")
    summary = st.session_state.event_logger.get_event_summary(days=7)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Events (7d)", summary['total_events'])
    with col2:
        st.metric("Active Days", summary['unique_days'])
    
    st.markdown("---")
    
    # Update memories button
    if st.button("🔄 Update Memory Insights", use_container_width=True):
        with st.spinner("Analyzing patterns..."):
            new_insights = st.session_state.memory_engine.update_memories()
            if new_insights.get('new_insights'):
                st.success(f"Found {len(new_insights['new_insights'])} new insights!")
            else:
                st.info("No new patterns detected yet")

# Main content
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🧠 ECHO")
st.caption("Your memory system learns your patterns over time")
st.markdown('</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Activity", "💭 AI Reflections", "📈 Patterns & Insights", "💬 Chat with ECHO"])

# Tab 1: Log Activity
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Log Your Activity")
        
        with st.form("log_activity_form"):
            event_type = st.selectbox(
                "Activity Type",
                ["note", "task", "coding", "meeting", "learning", "exercise", "other"]
            )
            
            content = st.text_area("Description", placeholder="What are you doing?")
            
            col_dur, col_tags = st.columns(2)
            with col_dur:
                duration = st.number_input("Duration (minutes)", min_value=0, max_value=480, value=30)
            with col_tags:
                tags_input = st.text_input("Tags (comma-separated)", placeholder="work, focus, important")
            
            submitted = st.form_submit_button("💾 Save Activity", use_container_width=True)
            
            if submitted and content:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                event_id = st.session_state.event_logger.log_event(
                    event_type=event_type,
                    content=content,
                    duration_minutes=duration,
                    tags=tags
                )
                st.success(f"✓ Activity logged! (ID: {event_id})")
                st.balloons()
            elif submitted:
                st.warning("Please enter a description")
    
    with col2:
        st.subheader("Recent Activities")
        recent = st.session_state.event_logger.get_events(limit=5)
        if not recent.empty:
            for _, row in recent.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="insight-card">
                        <small>{row['timestamp'].strftime('%H:%M')}</small><br>
                        <strong>{row['event_type']}</strong>: {row['content'][:50]}<br>
                        <small>⏱️ {row['duration_minutes']} min</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No activities logged yet. Start by logging your first activity!")

# Tab 2: AI Reflections
with tab2:
    st.subheader("💭 ECHO's Reflections")
    
    # Generate reflection button
    col1, col2 = st.columns([1, 3])
    with col1:
        focus_area = st.selectbox(
            "Focus Area",
            ["general", "productivity", "consistency", "patterns"]
        )
        
        if st.button("✨ Generate New Reflection", use_container_width=True):
            with st.spinner("ECHO is thinking..."):
                reflection = st.session_state.ai_reflection.generate_reflection(focus=focus_area)
                st.session_state.current_reflection = reflection
    
    with col2:
        if 'current_reflection' in st.session_state:
            st.markdown(f"""
            <div class="insight-card">
                <h4>🧠 ECHO says:</h4>
                <p style="font-size: 1.1rem;">{st.session_state.current_reflection}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Click the button to generate a personalized reflection based on your patterns!")
    
    # Weekly summary
    st.markdown("---")
    st.subheader("📅 Weekly Summary")
    if st.button("📊 Generate Weekly Summary"):
        summary = st.session_state.ai_reflection.generate_weekly_summary()
        st.markdown(f"""
        <div class="insight-card">
            {summary}
        </div>
        """, unsafe_allow_html=True)

# Tab 3: Patterns & Insights
with tab3:
    st.subheader("📈 Behavioral Patterns")
    
    # Get latest patterns
    patterns = st.session_state.memory_engine.user_profile.get("behavioral_patterns", {})
    
    if patterns:
        # Display patterns in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⏰ Time Patterns")
            hourly = patterns.get("hourly", {})
            if hourly.get("peak_hours"):
                st.info(f"**Peak Hours:** {', '.join([f'{h}:00' for h in hourly['peak_hours'][:3]])}")
            if hourly.get("most_active_hour"):
                st.info(f"**Most Active:** {hourly['most_active_hour']}:00")
            
            st.markdown("### 📅 Weekly Patterns")
            weekly = patterns.get("weekly", {})
            if weekly.get("most_productive_day"):
                st.success(f"**Most Productive Day:** {weekly['most_productive_day']}")
            if weekly.get("consistency_score"):
                score = weekly['consistency_score']
                st.metric("Consistency Score", f"{score:.0%}", 
                         delta="High" if score > 0.7 else "Low" if score < 0.3 else "Medium")
            if weekly.get("trend"):
                st.info(f"**Trend:** {weekly['trend'].capitalize()} (strength: {weekly.get('trend_strength', 0):.0%})")
        
        with col2:
            st.markdown("### ⚡ Activity Bursts")
            burst_lull = patterns.get("burst_lull", {})
            if burst_lull.get("peak_hourly_activity"):
                st.metric("Peak Hourly Activity", f"{burst_lull['peak_hourly_activity']} events")
            if burst_lull.get("avg_hourly_activity"):
                st.metric("Avg Hourly Activity", f"{burst_lull['avg_hourly_activity']:.1f} events")
            
            st.markdown("### 🧠 Memory Clusters")
            clusters = st.session_state.memory_engine.user_profile.get("memory_clusters", [])
            if clusters:
                top_clusters = sorted(clusters, key=lambda x: x['event_count'], reverse=True)[:3]
                for cluster in top_clusters:
                    st.caption(f"• {cluster['name']}: {cluster['event_count']} events")
        
        # Activity timeline chart
        st.markdown("---")
        st.subheader("📊 Activity Timeline")
        
        # Get rolling metrics
        rolling_df = st.session_state.temporal_engine.calculate_rolling_metrics()
        if not rolling_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=rolling_df.index,
                y=rolling_df['count'],
                mode='lines+markers',
                name='Daily Activity',
                line=dict(color='#667eea', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=rolling_df.index,
                y=rolling_df['rolling_7d'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='#764ba2', width=3, dash='dash')
            ))
            fig.update_layout(
                title="Activity Over Time",
                xaxis_title="Date",
                yaxis_title="Number of Events",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data yet. Keep logging activities to see your patterns emerge!")

# Tab 4: Chat Interface
with tab4:
    st.subheader("💬 Chat with ECHO")
    st.caption("Ask me about your patterns, productivity, or any insights!")
    
    # Chat input
    user_question = st.text_input("You:", placeholder="e.g., 'How productive was I this week?' or 'When do I focus best?'")
    
    if user_question:
        # Add to chat history
        st.session_state.chat_history.append(("user", user_question))
        
        # Get response
        with st.spinner("ECHO is thinking..."):
            response = st.session_state.query_interface.answer_query(user_question)
            st.session_state.chat_history.append(("echo", response))
    
    # Display chat history
    for role, message in st.session_state.chat_history[-10:]:  # Show last 10 messages
        if role == "user":
            st.markdown(f'<div class="chat-message user-message">🙋 <strong>You:</strong> {message}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message echo-message">🧠 <strong>ECHO:</strong> {message}</div>', 
                       unsafe_allow_html=True)
    
    # Quick question buttons
    st.markdown("---")
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("📊 How productive was I this week?"):
        response = st.session_state.query_interface.answer_query("How productive was I this week?")
        st.session_state.chat_history.append(("echo", response))
        st.rerun()
    
    if col2.button("⏰ When do I focus best?"):
        response = st.session_state.query_interface.answer_query("When do I focus best?")
        st.session_state.chat_history.append(("echo", response))
        st.rerun()
    
    if col3.button("📈 What patterns do you see?"):
        response = st.session_state.query_interface.answer_query("What patterns do you see in my behavior?")
        st.session_state.chat_history.append(("echo", response))
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*ECHO learns from your patterns over time. The more you log, the smarter the insights!* 🧠")