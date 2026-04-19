# app.py
"""
ECHO - Personal AI Memory System
Dribbble-Inspired UI/UX with Persistent Chat History & Fixed Text Colors
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time
import random
from modules import EventLogger, TemporalEngine, MemoryEngine, AIReflection, QueryInterface
from modules.gamification import Gamification
from modules.report_generator import ReportGenerator
from modules.notifications import NotificationManager
from modules.chat_storage import ChatStorage

# Page configuration
st.set_page_config(
    page_title="ECHO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DRIBBBLE-INSPIRED THEME WITH FIXED TEXT COLORS
# ============================================

COLORS = {
    "dark": {
        "bg": "#0D0D0D",
        "surface": "#1A1A1A",
        "surface_2": "#242424",
        "surface_3": "#2A2A2A",
        "border": "rgba(255,255,255,0.05)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#C0C0C0",
        "text_tertiary": "#A0A0A0",
        "accent_pink": "#FF2D7A",
        "accent_purple": "#B826E8",
        "accent_blue": "#2D7AFF",
        "success": "#00E5A0",
        "gradient_1": "linear-gradient(135deg, #FF2D7A 0%, #B826E8 100%)",
        "gradient_2": "linear-gradient(135deg, #2D7AFF 0%, #B826E8 100%)",
    },
    "light": {
        "bg": "#F5F5F7",
        "surface": "#FFFFFF",
        "surface_2": "#F8F8FA",
        "surface_3": "#F0F0F2",
        "border": "rgba(0,0,0,0.06)",
        "text_primary": "#000000",
        "text_secondary": "#444444",
        "text_tertiary": "#666666",
        "accent_pink": "#FF2D7A",
        "accent_purple": "#B826E8",
        "accent_blue": "#2D7AFF",
        "success": "#00C48C",
        "gradient_1": "linear-gradient(135deg, #FF2D7A 0%, #B826E8 100%)",
        "gradient_2": "linear-gradient(135deg, #2D7AFF 0%, #B826E8 100%)",
    }
}

if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

c = COLORS[st.session_state.theme]

def apply_dribbble_style():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100..900;1,100..900&family=SF+Pro+Display:wght@400;500;600;700&display=swap');

    .stApp {{
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0a0e27 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }}

    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}

    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}

    .app-header {{
        margin-bottom: 2rem;
        text-align: left;
    }}

    .app-header h1 {{
        font-size: 2.5rem;
        font-weight: 700;
        background: {c['gradient_1']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }}

    .app-header p {{
        color: {c['text_secondary']};
        font-size: 0.875rem;
    }}

    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }}

    .stat-card {{
        background: {c['surface']};
        border-radius: 20px;
        padding: 1.25rem;
        border: 1px solid {c['border']};
        transition: all 0.2s ease;
    }}

    .stat-card:hover {{
        transform: translateY(-2px);
        background: {c['surface_2']};
    }}

    .stat-label {{
        color: {c['text_secondary']};
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}

    .stat-value {{
        color: {c['text_primary']};
        font-size: 1.75rem;
        font-weight: 700;
    }}

    .form-card {{
        background: {c['surface']};
        border-radius: 24px;
        padding: 1.5rem;
        border: 1px solid {c['border']};
        margin-bottom: 1.5rem;
    }}

    .section-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {c['text_primary']};
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .activity-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }}

    .activity-btn {{
        background: {c['surface_2']};
        border: 1px solid {c['border']};
        border-radius: 16px;
        padding: 0.75rem;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
    }}

    .activity-btn:hover {{
        background: {c['surface_3']};
        transform: translateY(-2px);
        border-color: {c['accent_pink']};
    }}

    .activity-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }}

    .activity-name {{
        color: {c['text_secondary']};
        font-size: 0.7rem;
        font-weight: 500;
    }}

    .chat-container {{
        background: {c['surface']};
        border-radius: 24px;
        border: 1px solid {c['border']};
        height: 450px;
        overflow-y: auto;
        padding: 0.75rem 1rem;
        margin-top: 0;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}

    .chat-container > div:empty,
    .chat-container > div > div:empty {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    .chat-container .stMarkdown {{
        width: 100%;
    }}

    .chat-container > div {{
        gap: 0 !important;
    }}

    .chat-container .message:first-child {{
        margin-top: 0;
        padding-top: 0;
    }}

    .message {{
        display: flex;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease;
    }}

    .message.user {{
        justify-content: flex-end;
    }}

    .message-content {{
        max-width: 75%;
        padding: 0.75rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        line-height: 1.4;
    }}

    .message.user .message-content {{
        background: {c['gradient_1']};
        color: white;
        border-bottom-right-radius: 4px;
    }}

    .message.echo .message-content {{
        background: {c['surface_2']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-bottom-left-radius: 4px;
    }}

    .stTabs {{
        margin-top: -0.5rem;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        margin-bottom: 0;
    }}

    .badge-card {{
        background: {c['surface_2']};
        border-radius: 16px;
        padding: 0.75rem;
        text-align: center;
        border: 1px solid {c['border']};
        transition: all 0.2s ease;
    }}

    .badge-card:hover {{
        transform: translateY(-2px);
        border-color: {c['accent_pink']};
    }}

    [data-testid="stSidebar"] {{
        background: {c['surface']};
        border-right: 1px solid {c['border']};
    }}

    [data-testid="stSidebar"] .stMarkdown {{
        color: {c['text_primary']};
    }}

    [data-testid="stSidebar"] .stCaption {{
        color: {c['text_secondary']};
    }}

    .stButton button {{
        background: {c['surface_2']};
        border: 1px solid {c['border']};
        border-radius: 30px;
        color: {c['text_primary']};
        transition: all 0.2s ease;
    }}

    .stButton button:hover {{
        background: {c['gradient_1']};
        border-color: transparent;
        color: white;
        transform: translateY(-1px);
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: {c['surface']};
        border-radius: 30px;
        padding: 0.25rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 30px;
        padding: 0.5rem 1rem;
        color: {c['text_secondary']};
        font-weight: 500;
    }}

    .stTabs [aria-selected="true"] {{
        background: {c['gradient_1']};
        color: white;
    }}

    h1, h2, h3, h4, h5, h6, label, .stMarkdown {{
        color: {c['text_primary']} !important;
    }}

    .stMetric label, .stMetric .stMarkdown {{
        color: {c['text_secondary']} !important;
    }}

    .stAlert {{
        background: {c['surface_2']};
        border-color: {c['border']};
        color: {c['text_primary']};
    }}

    .stSelectbox label, .stTextInput label, .stTextArea label {{
        color: {c['text_secondary']} !important;
    }}

    .stSlider label {{
        color: {c['text_secondary']} !important;
    }}

    .stCheckbox label {{
        color: {c['text_primary']} !important;
    }}

  /* Force expander text colors for dark/light mode */
.streamlit-expanderHeader {{
    background: {c['surface_2']} !important;
    border-radius: 16px !important;
    color: {c['text_primary']} !important;
}}

.streamlit-expanderHeader span {{
    color: {c['text_primary']} !important;
}}

.streamlit-expanderHeader p {{
    color: {c['text_primary']} !important;
}}

.streamlit-expanderContent {{
    color: {c['text_secondary']} !important;
}}

.streamlit-expanderContent p {{
    color: {c['text_primary']} !important;
}}

.streamlit-expanderContent div {{
    color: {c['text_primary']} !important;
}}

/* Also force markdown text inside expanders */
.streamlit-expanderContent .stMarkdown {{
    color: {c['text_primary']} !important;
}}

.streamlit-expanderContent .stMarkdown p {{
    color: {c['text_primary']} !important;
}}

    .stInfo, .stWarning, .stError, .stSuccess {{
        color: {c['text_primary']};
    }}

    .stCodeBlock {{
        background: {c['surface_2']};
        color: {c['text_primary']};
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background: {c['surface_2']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 16px !important;
        color: {c['text_primary']} !important;
    }}

    div[data-baseweb="select"] ul {{
        background: {c['surface']} !important;
    }}

    div[data-baseweb="select"] li {{
        color: {c['text_primary']} !important;
    }}

    div[data-baseweb="select"] li:hover {{
        background: {c['surface_2']} !important;
    }}

    .stTextInput input, .stTextArea textarea {{
        background: {c['surface_2']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 16px !important;
        color: {c['text_primary']} !important;
    }}

    .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
        color: {c['text_tertiary']};
    }}

    .stNumberInput input {{
        background: {c['surface_2']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 16px !important;
        color: {c['text_primary']} !important;
    }}

    .stCheckbox {{
        color: {c['text_primary']};
    }}

    .stProgress > div > div > div > div {{
        color: {c['text_primary']};
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    ::-webkit-scrollbar {{
        width: 4px;
    }}

    ::-webkit-scrollbar-track {{
        background: {c['surface_2']};
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb {{
        background: {c['accent_pink']};
        border-radius: 4px;
    }}
    </style>
    
    """, unsafe_allow_html=True)
    

apply_dribbble_style()

# ============================================
# INITIALIZE SESSION STATE
# ============================================

if 'initialized' not in st.session_state:
    with st.spinner("🧠 Initializing ECHO..."):
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
        st.session_state.gamification = Gamification(
            st.session_state.event_logger,
            st.session_state.memory_engine
        )
        st.session_state.report_generator = ReportGenerator(
            st.session_state.event_logger,
            st.session_state.memory_engine,
            st.session_state.ai_reflection
        )
        st.session_state.notification_manager = NotificationManager()
        st.session_state.chat_storage = ChatStorage()
        st.session_state.chat_history = st.session_state.chat_storage.get_today_messages()

        removed = st.session_state.chat_storage.clear_old_messages()
        if removed > 0:
            print(f"Cleared {removed} old messages from chat history")

        st.session_state.sarcasm_mode = True

        new_badges = st.session_state.gamification.check_and_award_badges()
        if new_badges:
            st.session_state.new_badges = new_badges

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem 0 1rem;">
        <div style="font-size: 2.5rem;">🧠</div>
        <h2 style="margin: 0.5rem 0 0; color: {c['text_primary']};">ECHO</h2>
        <p style="color: {c['text_tertiary']}; font-size: 0.7rem;">Personal AI Memory</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🎨 Theme")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "dark"
            st.rerun()
    with col2:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.theme = "light"
            st.rerun()

    st.markdown("---")

    stats = st.session_state.gamification.get_statistics()
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
            <span style="color: {c['text_secondary']};">Level</span>
            <span style="color: {c['text_primary']}; font-weight: 600;">{stats['level']}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
            <span style="color: {c['text_secondary']};">Streak</span>
            <span style="color: {c['text_primary']}; font-weight: 600;">{stats['streak']} days</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: {c['text_secondary']};">Badges</span>
            <span style="color: {c['text_primary']}; font-weight: 600;">{stats['badges_earned']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("💬 Chat")
    message_count = st.session_state.chat_storage.get_message_count_today()
    st.caption(f"📝 {message_count} messages today")
    st.caption(f"⏰ Messages saved for 24 hours")

    st.markdown("---")

    st.markdown(f"<p style='color: {c['text_secondary']}; font-size: 0.7rem; margin-bottom: 0.5rem;'>PERSONALITY</p>", unsafe_allow_html=True)

    current = st.session_state.query_interface.personality_manager.get_personality_info()
    personality_option = st.selectbox(
        "",
        options=["mentor", "friend", "well_wisher", "sarcastic"],
        format_func=lambda x: {
            "mentor": "🎓 Mentor",
            "friend": "👋 Friend",
            "well_wisher": "💝 Well-Wisher",
            "sarcastic": "🎭 Sarcastic"
        }[x],
        index=["mentor", "friend", "well_wisher", "sarcastic"].index(current['current']),
        label_visibility="collapsed"
    )

    if personality_option != current['current']:
        st.session_state.query_interface.set_personality(personality_option)
        st.rerun()

    st.markdown("---")

    st.subheader("🔔 Notifications")
    if 'notifications_enabled' not in st.session_state:
        st.session_state.notifications_enabled = True

    st.session_state.notifications_enabled = st.toggle(
        "Enable",
        value=st.session_state.notifications_enabled,
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.session_state.sarcasm_mode = st.toggle(
        "🎭 Sarcasm Mode",
        value=st.session_state.sarcasm_mode
    )

    if st.button("🔄 Sync Memories", use_container_width=True):
        with st.spinner("Analyzing..."):
            new_insights = st.session_state.memory_engine.update_memories()
            if new_insights.get('new_insights'):
                st.toast(f"✨ {len(new_insights['new_insights'])} new insights!", icon="💡")

# ============================================
# MAIN CONTENT
# ============================================

st.markdown(f"""
<div class="app-header">
    <h1>ECHO</h1>
    <p>Your personal AI memory system</p>
</div>
""", unsafe_allow_html=True)

# Stats Grid - Clickable cards that navigate to tabs
summary = st.session_state.event_logger.get_event_summary(days=7)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(f"📊\n{stats['total_events']}\nTotal Events", use_container_width=True, key="stat_total"):
        st.session_state.nav_target = "Log Activity"
        st.rerun()

with col2:
    if st.button(f"📅\n{summary['total_events']}\nThis Week\n{summary['unique_days']} active days", use_container_width=True, key="stat_week"):
        st.session_state.nav_target = "Log Activity"
        st.rerun()

with col3:
    if st.button(f"⭐\n{stats['level']}\nCurrent Level", use_container_width=True, key="stat_level"):
        st.session_state.nav_target = "Profile"
        st.rerun()

with col4:
    if st.button(f"🏆\n{stats['badges_earned']}\nBadges", use_container_width=True, key="stat_badges"):
        st.session_state.nav_target = "Profile"
        st.rerun()

# Quick Actions - Clickable buttons that open the log form with preselected type
st.markdown(f"""
<div class="form-card">
    <div class="section-title">
        <span>⚡</span> Quick Log
    </div>
    <div class="activity-grid">
""", unsafe_allow_html=True)

quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

with quick_col1:
    if st.button("💻\nCoding", use_container_width=True, key="quick_coding"):
        st.session_state.nav_target = "Log Activity"
        st.session_state.preselected_type = "coding"
        st.session_state.scroll_to_form = True
        st.rerun()

with quick_col2:
    if st.button("📝\nNote", use_container_width=True, key="quick_note"):
        st.session_state.nav_target = "Log Activity"
        st.session_state.preselected_type = "note"
        st.session_state.scroll_to_form = True
        st.rerun()

with quick_col3:
    if st.button("✅\nTask", use_container_width=True, key="quick_task"):
        st.session_state.nav_target = "Log Activity"
        st.session_state.preselected_type = "task"
        st.session_state.scroll_to_form = True
        st.rerun()

with quick_col4:
    if st.button("📚\nLearn", use_container_width=True, key="quick_learn"):
        st.session_state.nav_target = "Log Activity"
        st.session_state.preselected_type = "learning"
        st.session_state.scroll_to_form = True
        st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)

# Tabs - NEW ORDER: Log Activity → Chat → Reflections → Insights → Profile
tab_titles = ["📝 Log Activity", "💬 Chat", "💭 Reflections", "📊 Insights", "🏆 Profile"]

# Determine which tab to show based on nav_target
if 'nav_target' in st.session_state and st.session_state.nav_target:
    if st.session_state.nav_target == "Log Activity":
        default_tab = 0
    elif st.session_state.nav_target == "Profile":
        default_tab = 4
    else:
        default_tab = 0
    st.session_state.nav_target = None
else:
    default_tab = 0

tabs = st.tabs(tab_titles)

# ============================================
# TAB 0: LOG ACTIVITY - WITH AUTO-SCROLL
# ============================================

with tabs[0]:
    st.markdown('<div id="log-form"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="form-card">
        <div class="section-title">📝 Log Your Activity</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("log_form"):
            event_types = ["coding", "note", "task", "meeting", "learning", "exercise", "other"]
            
            default_index = 0
            if hasattr(st.session_state, 'preselected_type') and st.session_state.preselected_type in event_types:
                default_index = event_types.index(st.session_state.preselected_type)
                delattr(st.session_state, 'preselected_type')
            
            event_type = st.selectbox(
                "Activity Type",
                event_types,
                format_func=lambda x: f"📌 {x.title()}",
                index=default_index
            )
            content = st.text_area("What are you doing?", placeholder="Describe your activity...", key="activity_content")
            duration = st.slider("Duration (minutes)", 5, 240, 30)
            tags = st.text_input("Tags", placeholder="work, focus, important")
            
            submitted = st.form_submit_button("Save Activity", use_container_width=True)
            
            if submitted:
                if content:
                    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
                    st.session_state.event_logger.log_event(event_type, content, duration, tags_list)
                    st.toast(f"✓ {event_type.title()} logged!", icon="✅")
                    st.balloons()
                    
                    new_badges = st.session_state.gamification.check_and_award_badges()
                    if new_badges:
                        st.session_state.new_badges = new_badges
                    
                    if hasattr(st.session_state, 'scroll_to_form'):
                        delattr(st.session_state, 'scroll_to_form')
                    
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.toast("Please enter a description", icon="⚠️")
    
    with col2:
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📋 Recent</div>
        </div>
        """, unsafe_allow_html=True)
        recent = st.session_state.event_logger.get_events(limit=5)
        if not recent.empty:
            for _, row in recent.iterrows():
                st.markdown(f"""
                <div style="background: {c['surface_2']}; border-radius: 16px; padding: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="color: {c['text_tertiary']}; font-size: 0.65rem;">{row['timestamp'].strftime('%I:%M %p')}</div>
                    <div style="color: {c['text_primary']}; font-size: 0.8rem;">{row['content'][:60]}</div>
                    <div style="color: {c['text_tertiary']}; font-size: 0.65rem;">⏱️ {row['duration_minutes']} min</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activities yet. Log your first one above!")

if hasattr(st.session_state, 'scroll_to_form') and st.session_state.scroll_to_form:
    st.markdown("""
    <script>
        var element = document.getElementById('log-form');
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    </script>
    """, unsafe_allow_html=True)
    delattr(st.session_state, 'scroll_to_form')

# ============================================
# TAB 1: CHAT
# ============================================

with tabs[1]:
    current = st.session_state.query_interface.personality_manager.get_personality_info()

    st.markdown("""
    <style>
    .chat-container > div { gap: 0 !important; margin: 0 !important; }
    .chat-container > div > div:empty,
    .chat-container > div:empty { display: none !important; height: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.chat_history:
        messages_html = ""
        for role, message in st.session_state.chat_history[-20:]:
            if role == "user":
                messages_html += f"""
                <div class="message user">
                    <div class="message-content">{message}</div>
                </div>"""
            else:
                messages_html += f"""
                <div class="message echo">
                    <div class="message-content">{message}</div>
                </div>"""
    else:
        messages_html = f"""
        <div style="text-align: center; padding: 2rem; color: {c['text_tertiary']};">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
            <div>No messages yet today</div>
            <div style="font-size: 0.75rem;">Start a conversation with {current['name']}!</div>
        </div>"""

    st.markdown(f'<div class="chat-container">{messages_html}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "", placeholder=f"Ask {current['name']} anything...",
            key="chat_input", label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("Send", use_container_width=True, key="send_button")

    if send_button and user_input:
        st.session_state.chat_storage.add_message("user", user_input)
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner(f"{current['details']['icon']} {current['name']} is thinking..."):
            response = st.session_state.query_interface.answer_query_with_personality(user_input)
            st.session_state.chat_storage.add_message("echo", response)
            st.session_state.chat_history.append(("echo", response))

        st.rerun()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🗑️ Clear Today's Chat", use_container_width=True):
            st.session_state.chat_storage = ChatStorage()
            st.session_state.chat_history = []
            st.toast("Chat history cleared for today!", icon="🗑️")
            st.rerun()

# ============================================
# TAB 2: REFLECTIONS
# ============================================

with tabs[2]:
    has_data = len(st.session_state.event_logger.get_events()) > 0
    
    if not has_data:
        st.markdown(f"""
        <div class="form-card" style="text-align: center;">
            <div class="section-title">💭 Reflections</div>
            <div style="font-size: 3rem; margin: 1rem 0;">✨</div>
            <h3>Your reflection space is waiting...</h3>
            <p style="color: {c['text_secondary']};">Log your first activity to unlock personalized insights!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">🔮 What you'll see here</div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <div style="background: {c['surface_2']}; border-radius: 16px; padding: 0.75rem;">
                    <div style="font-size: 1.5rem;">📊</div>
                    <div style="font-weight: 500;">Productivity Reports</div>
                    <div style="font-size: 0.75rem; color: {c['text_tertiary']};">Weekly summaries</div>
                </div>
                <div style="background: {c['surface_2']}; border-radius: 16px; padding: 0.75rem;">
                    <div style="font-size: 1.5rem;">🎯</div>
                    <div style="font-weight: 500;">Pattern Recognition</div>
                    <div style="font-size: 0.75rem; color: {c['text_tertiary']};">Peak hours, best days</div>
                </div>
                <div style="background: {c['surface_2']}; border-radius: 16px; padding: 0.75rem;">
                    <div style="font-size: 1.5rem;">💡</div>
                    <div style="font-weight: 500;">AI Insights</div>
                    <div style="font-size: 0.75rem; color: {c['text_tertiary']};">Personalized advice</div>
                </div>
                <div style="background: {c['surface_2']}; border-radius: 16px; padding: 0.75rem;">
                    <div style="font-size: 1.5rem;">🏆</div>
                    <div style="font-weight: 500;">Celebrations</div>
                    <div style="font-size: 0.75rem; color: {c['text_tertiary']};">Milestone achievements</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Log Your First Activity", use_container_width=True):
            st.session_state.nav_target = "Log Activity"
            st.rerun()
    
    else:
        stats = st.session_state.gamification.get_statistics()
        summary = st.session_state.event_logger.get_event_summary(days=7)
        
        hour = datetime.now().hour
        if hour < 12:
            time_greeting = "morning"
            emoji = "🌅"
        elif hour < 18:
            time_greeting = "afternoon"
            emoji = "☀️"
        else:
            time_greeting = "evening"
            emoji = "🌙"
        
        quotes = [
            ("✨", "Small daily improvements lead to massive results over time."),
            ("💪", "You don't have to be perfect. You just have to show up."),
            ("🎯", "Focus on progress, not perfection."),
            ("🌟", "Every task you log is a step toward your goals."),
            ("📈", "Consistency beats intensity. Keep showing up!"),
            ("🧠", "Your future self will thank you for the work you do today."),
            ("💫", "The only bad workout is the one that didn't happen."),
        ]
        quote_emoji, quote_text = random.choice(quotes)
        
        st.markdown(f"""
        <div class="form-card" style="text-align: center;">
            <div class="section-title">💭 Good {time_greeting}! {emoji}</div>
            <div style="font-size: 1.2rem; margin: 0.5rem 0;">"{quote_text}"</div>
            <div style="font-size: 0.8rem; color: {c['text_tertiary']};">— ECHO</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📊 Quick Glance</div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                <div>
                    <div style="font-size: 2rem;">📝</div>
                    <div style="font-size: 1.5rem; font-weight: 700;">{summary['total_events']}</div>
                    <div style="font-size: 0.7rem; color: {c['text_tertiary']};">activities this week</div>
                </div>
                <div>
                    <div style="font-size: 2rem;">🔥</div>
                    <div style="font-size: 1.5rem; font-weight: 700;">{stats['streak']}</div>
                    <div style="font-size: 0.7rem; color: {c['text_tertiary']};">day streak</div>
                </div>
                <div>
                    <div style="font-size: 2rem;">⭐</div>
                    <div style="font-size: 1.5rem; font-weight: 700;">{stats['level']}</div>
                    <div style="font-size: 0.7rem; color: {c['text_tertiary']};">current level</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">🧠 ECHO's Reflection</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            focus = st.selectbox(
                "Focus Area",
                ["General", "Productivity", "Consistency", "Patterns", "Motivation"],
                key="focus_select"
            )
            
            if st.button("✨ Generate Reflection", use_container_width=True):
                with st.spinner("ECHO is reflecting..."):
                    if focus == "Motivation":
                        reflection = st.session_state.ai_reflection.generate_motivational_reflection()
                    else:
                        reflection = st.session_state.ai_reflection.generate_reflection(focus.lower())
                    st.session_state.current_reflection = reflection
        
        with col2:
            if 'current_reflection' in st.session_state:
                st.markdown(f"""
                <div style="background: {c['surface_2']}; border-radius: 20px; padding: 1.25rem; border-left: 4px solid {c['accent_pink']};">
                    <div style="color: {c['text_primary']}; font-size: 0.95rem; line-height: 1.6;">
                        {st.session_state.current_reflection}
                    </div>
                    <div style="margin-top: 0.75rem; font-size: 0.7rem; color: {c['text_tertiary']};">
                        — generated just for you
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: {c['surface_2']}; border-radius: 20px; padding: 1.25rem; text-align: center; color: {c['text_tertiary']};">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
                    <div>Click the button to hear what ECHO thinks about your patterns!</div>
                    <div style="font-size: 0.75rem; margin-top: 0.5rem;">Based on your actual activity data</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📅 Weekly Snapshot</div>
        </div>
        """, unsafe_allow_html=True)
        
        week_ago = datetime.now() - timedelta(days=7)
        df_week = st.session_state.event_logger.get_events(start_date=week_ago)
        
        if not df_week.empty:
            total_week = len(df_week)
            unique_days = df_week['date'].nunique()
            top_activity = df_week['event_type'].mode().iloc[0] if not df_week.empty else "None"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Activities", total_week)
            with col2:
                st.metric("Active Days", unique_days)
            with col3:
                st.metric("Top Activity", top_activity.title())
            
            if st.button("📊 Generate Full Weekly Summary", use_container_width=True):
                summary_text = st.session_state.ai_reflection.generate_weekly_summary()
                st.markdown(f"""
                <div style="background: {c['surface_2']}; border-radius: 16px; padding: 1rem; margin-top: 1rem;">
                    {summary_text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activities this week. Start logging to see your weekly snapshot!")
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">🏆 Recent Achievement</div>
        </div>
        """, unsafe_allow_html=True)
        
        earned_badges = st.session_state.gamification.get_earned_badges()
        if earned_badges:
            latest_badge = earned_badges[-1]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {c['accent_pink']}20, {c['accent_purple']}20); border-radius: 16px; padding: 1rem; display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 3rem;">🏅</div>
                <div>
                    <div style="font-weight: 600; color: {c['text_primary']};">{latest_badge['name']}</div>
                    <div style="font-size: 0.8rem; color: {c['text_secondary']};">{latest_badge['description']}</div>
                    <div style="font-size: 0.7rem; color: {c['text_tertiary']};">Earned recently!</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("✨ Complete activities to earn your first badge!")
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📝 Daily Reflection Prompt</div>
            <p style="color: {c['text_secondary']};">Take a moment to think about:</p>
            <div style="background: {c['surface_2']}; border-radius: 16px; padding: 1rem; margin-top: 0.5rem; font-style: italic; color: {c['text_primary']};">
                "What was one thing you accomplished today that you're proud of?"
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# TAB 3: INSIGHTS
# ============================================

with tabs[3]:
    patterns = st.session_state.memory_engine.user_profile.get("behavioral_patterns", {})
    
    if patterns and patterns.get("hourly", {}).get("peak_hours"):
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">⏰ Your Peak Hours</div>
        </div>
        """, unsafe_allow_html=True)
        
        hourly = patterns.get("hourly", {})
        if hourly.get("peak_hours"):
            peak_hours = hourly['peak_hours'][:3]
            peak_hours_str = ", ".join([f"{h}:00" for h in peak_hours])
            
            st.info(f"📈 You're most productive at: **{peak_hours_str}**")
            
            if st.button("💡 Get Recommendation for Peak Hours", use_container_width=True):
                st.success(f"Schedule your most important tasks between {peak_hours[0]}:00 and {peak_hours[0]+2}:00 for maximum productivity!")
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📅 Your Best Day</div>
        </div>
        """, unsafe_allow_html=True)
        
        weekly = patterns.get("weekly", {})
        if weekly.get("most_productive_day"):
            best_day = weekly['most_productive_day']
            st.success(f"⭐ Your most productive day is **{best_day}**")
            
            if st.button("📅 Plan Your Week", use_container_width=True):
                st.info(f"Try scheduling your deep work sessions on {best_day}s when you're naturally more productive!")
        
        if weekly.get("consistency_score"):
            score = weekly['consistency_score']
            st.markdown(f"""
            <div class="form-card">
                <div class="section-title">🎯 Consistency Score</div>
            </div>
            """, unsafe_allow_html=True)
            
            if score > 0.7:
                st.success(f"✅ Your consistency score is {score:.0%} - Excellent! Keep maintaining your routine.")
                if st.button("🏆 Maintain Your Streak"):
                    st.info("You're doing great! Try to log at least one activity every day to keep your streak alive!")
            elif score > 0.4:
                st.warning(f"📊 Your consistency score is {score:.0%} - Good, but can improve.")
                if st.button("📈 Improve Consistency"):
                    st.info("Try logging activities at the same time each day to build a stronger routine!")
            else:
                st.error(f"⚠️ Your consistency score is {score:.0%} - Needs improvement.")
                if st.button("🎯 Set a Daily Goal"):
                    st.info("Start with a simple goal: log just ONE activity every day for the next 7 days!")
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📊 Activity Timeline</div>
        </div>
        """, unsafe_allow_html=True)
        
        rolling_df = st.session_state.temporal_engine.calculate_rolling_metrics()
        if not rolling_df.empty:
            fig = go.Figure()
            
            if st.session_state.theme == "dark":
                line_color = '#818cf8'
                grid_color = '#374151'
                text_color = '#e0e0e0'
            else:
                line_color = '#667eea'
                grid_color = '#e5e7eb'
                text_color = '#1f2937'
            
            fig.add_trace(go.Scatter(
                x=rolling_df.index,
                y=rolling_df['count'],
                mode='lines+markers',
                name='Daily Activity',
                line=dict(color=line_color, width=2),
                marker=dict(size=6, color=line_color)
            ))
            fig.add_trace(go.Scatter(
                x=rolling_df.index,
                y=rolling_df['rolling_7d'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='#f59e0b', width=3, dash='dash')
            ))
            fig.update_layout(
                title="Activity Over Time",
                xaxis_title="Date",
                yaxis_title="Number of Events",
                height=400,
                hovermode='x unified',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color),
                xaxis=dict(gridcolor=grid_color, showgrid=True),
                yaxis=dict(gridcolor=grid_color, showgrid=True)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if len(rolling_df) > 7:
                recent_avg = rolling_df['count'].tail(7).mean()
                previous_avg = rolling_df['count'].tail(14).head(7).mean()
                if recent_avg > previous_avg * 1.1:
                    st.success("📈 You're on an upward trend! Keep up the great work!")
                elif recent_avg < previous_avg * 0.9:
                    st.warning("📉 Your activity has decreased recently. Time for a reset?")
                else:
                    st.info("➡️ Your activity is stable. Consistency is key!")
        
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">⏰ Your Memory Timeline</div>
        </div>
        """, unsafe_allow_html=True)
        
        evolution = st.session_state.memory_engine.user_profile.get("evolution_tracking", [])
        if evolution:
            for ev in evolution[-5:]:
                timestamp = datetime.fromisoformat(ev['timestamp']).strftime('%b %d, %Y')
                changes = ev.get('changes', [])
                for change in changes:
                    if change['type'] == 'productivity_increase':
                        st.success(f"📈 {timestamp}: {change['description']}")
                        if st.button(f"✨ Celebrate this win", key=f"celebrate_{timestamp}"):
                            st.balloons()
                            st.toast("Great job! Keep building this momentum! 🎉", icon="🎉")
                    elif change['type'] == 'productivity_decrease':
                        st.warning(f"📉 {timestamp}: {change['description']}")
                        if st.button(f"💪 Get back on track", key=f"recover_{timestamp}"):
                            st.info("Every day is a new opportunity. Start with one small task today!")
                    elif change['type'] == 'peak_hour_shift':
                        st.info(f"⏰ {timestamp}: {change['description']}")
        else:
            st.info("Your memory timeline will appear here as patterns emerge over time.")
            st.caption("💡 Log more activities to see how your behavior evolves!")
    
    else:
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📊 Insights</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("📊 Not enough data yet to show insights!")
        
        st.markdown("""
        ### 🔍 How to unlock insights:
        
        | Action | Insights You'll Get |
        |--------|---------------------|
        | Log 5+ activities | See your peak productivity hours |
        | Log for 7+ days | See weekly patterns and best days |
        | Log 20+ activities | Get consistency scores and trends |
        | Maintain a streak | See your motivation timeline |
        
        💡 **Pro tip**: The more you log, the smarter your insights become!
        """)
        
        if st.button("📝 Go to Log Activity", use_container_width=True):
            st.session_state.nav_target = "Log Activity"
            st.rerun()

# ============================================
# TAB 4: PROFILE - WITH EXPANDABLE SECTIONS & FIXED THEME COLORS
# ============================================

with tabs[4]:
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🏆 View Your Badges", expanded=False):
            earned = st.session_state.gamification.get_earned_badges()
            if earned:
                for badge in earned:
                    st.markdown(f"""
                    <div style="background: {c['surface_2']}; border-radius: 16px; padding: 0.75rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                        <div style="font-size: 1.5rem;">🏅</div>
                        <div>
                            <div style="color: {c['text_primary']} !important; font-weight: 500; font-size: 0.85rem;">{badge['name']}</div>
                            <div style="color: {c['text_secondary']} !important; font-size: 0.65rem;">{badge['description']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="color: {c['text_secondary']} !important;">
                    ✨ No badges yet. Complete activities to earn your first badge!
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style="margin-top: 1rem; color: {c['text_secondary']} !important;">
                    **How to earn your first badges:**
                    - 🐦 **Early Bird**: Log 10 activities before 9 AM
                    - 🔥 **Streak Master**: Log for 7 days in a row
                    - 🎯 **Focus God**: 4+ hours of focused work in one day
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        with st.expander("📊 View Your Progress", expanded=False):
            level_info = st.session_state.gamification.get_level()
            st.progress(level_info['progress'] / 100, text=f"Level {level_info['current_level']} → {level_info['current_level'] + 1}")
            
            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {c['text_secondary']} !important;">Total Events</span>
                    <span style="color: {c['text_primary']} !important; font-weight: 600;">{stats['total_events']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {c['text_secondary']} !important;">Current Streak</span>
                    <span style="color: {c['text_primary']} !important; font-weight: 600;">{stats['streak']} days</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {c['text_secondary']} !important;">Longest Streak</span>
                    <span style="color: {c['text_primary']} !important; font-weight: 600;">{stats['streak']} days</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("👤 Account Information", expanded=False):
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <p style="color: {c['text_primary']} !important;"><strong>Name:</strong> ECHO User</p>
            <p style="color: {c['text_primary']} !important;"><strong>Member since:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
            <p style="color: {c['text_primary']} !important;"><strong>Total Sessions:</strong> {stats['total_events']}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================

st.markdown(f"""
<div style="text-align: center; padding: 2rem 0 1rem; color: {c['text_tertiary']}; font-size: 0.7rem;">
    ECHO — Personal AI Memory System
</div>
""", unsafe_allow_html=True)