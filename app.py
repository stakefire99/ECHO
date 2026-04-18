# app.py
"""
ECHO - Professional AI Memory System
Enterprise-grade UI/UX with Dynamic Background System
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time
from modules import EventLogger, TemporalEngine, MemoryEngine, AIReflection, QueryInterface
from modules.gamification import Gamification
from modules.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="ECHO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DYNAMIC BACKGROUND SYSTEM
# ============================================

# Initialize background settings
if 'background_style' not in st.session_state:
    st.session_state.background_style = "gradient_dark"

if 'custom_bg_url' not in st.session_state:
    st.session_state.custom_bg_url = ""

# Background options
BACKGROUNDS = {
    "gradient_dark": {
        "name": "🌙 Midnight Galaxy",
        "css": "linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0d1117 100%)",
        "preview": "🌌"
    },
    "gradient_light": {
        "name": "☀️ Morning Mist", 
        "css": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "preview": "🌅"
    },
    "forest": {
        "name": "🌲 Forest Calm",
        "css": "linear-gradient(135deg, #134e5e 0%, #71b280 100%)",
        "preview": "🌳"
    },
    "ocean": {
        "name": "🌊 Ocean Deep",
        "css": "linear-gradient(135deg, #000428 0%, #004e92 100%)",
        "preview": "🌊"
    },
    "sunset": {
        "name": "🎨 Sunset Glow",
        "css": "linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%)",
        "preview": "🌇"
    },
    "cherry": {
        "name": "🌸 Cherry Blossom",
        "css": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
        "preview": "🌸"
    },
    "aurora": {
        "name": "✨ Northern Lights",
        "css": "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        "preview": "🌌"
    },
    "coffee": {
        "name": "☕ Coffee Shop",
        "css": "linear-gradient(135deg, #3e2723 0%, #4e342e 100%)",
        "preview": "☕"
    },
    "neon": {
        "name": "🎮 Neon City",
        "css": "linear-gradient(135deg, #200122 0%, #6f0000 100%)",
        "preview": "🎮"
    }
}

# Aesthetic background URLs (from inspiration images)
AESTHETIC_BACKGROUNDS = {
    "🍂 New York Autumn": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9",
    "🌧️ Moody Vibes": "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d",
    "🌃 City Lights": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000",
    "☕ Coffee Shop": "https://images.unsplash.com/photo-1442512595331-e89e73853f31",
    "💧 Rainy Window": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0",
    "📜 Vintage Paper": "https://images.unsplash.com/photo-1507842217343-583bb7270b66",
    "🎀 Whisper Pink": "https://images.unsplash.com/photo-1521747116042-5a810fda9664",
    "🍂 Folklore Vibes": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
    "🌙 Evermore": "https://images.unsplash.com/photo-1518837695005-2083093ee35b",
    "🍁 Downtown Girl": "https://images.unsplash.com/photo-1444723121867-7a241cacace9"
}

def save_background_preference():
    """Save background preference to file"""
    prefs = {
        "background_style": st.session_state.background_style,
        "custom_bg_url": st.session_state.custom_bg_url
    }
    try:
        with open("data/background_prefs.json", "w") as f:
            json.dump(prefs, f)
    except Exception:
        pass

def load_background_preference():
    """Load background preference from file"""
    try:
        with open("data/background_prefs.json", "r") as f:
            prefs = json.load(f)
            st.session_state.background_style = prefs.get("background_style", "gradient_dark")
            st.session_state.custom_bg_url = prefs.get("custom_bg_url", "")
    except FileNotFoundError:
        pass

def apply_dynamic_background():
    """Apply the selected background"""
    if st.session_state.background_style == "custom" and st.session_state.custom_bg_url:
        bg_css = f"url('{st.session_state.custom_bg_url}') center/cover no-repeat fixed"
        overlay = "rgba(0,0,0,0.4)"
    else:
        bg_css = BACKGROUNDS.get(st.session_state.background_style, BACKGROUNDS["gradient_dark"])["css"]
        overlay = "rgba(0,0,0,0.2)" if "dark" in st.session_state.background_style or st.session_state.background_style in ["forest", "ocean", "aurora", "coffee", "neon"] else "rgba(255,255,255,0.1)"
    
    st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_css};
        transition: background 0.5s ease;
    }}
    
    /* Add overlay for better text readability */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: {overlay};
        pointer-events: none;
        z-index: 0;
    }}
    
    /* Make sure content is above overlay */
    .main-header, .stats-grid, .form-card, .chat-container, .activity-grid {{
        position: relative;
        z-index: 1;
    }}
    
    /* Smooth transition for all elements */
    * {{
        transition: all 0.2s ease;
    }}
    </style>
    """, unsafe_allow_html=True)

# ============================================
# PROFESSIONAL THEME SYSTEM
# ============================================

if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

# Load background preference
load_background_preference()

# Professional color palettes
COLORS = {
    "dark": {
        "bg": "#0A0A0A",
        "surface": "rgba(20, 20, 20, 0.95)",
        "surface_2": "rgba(28, 28, 30, 0.95)",
        "border": "rgba(255,255,255,0.08)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#98989E",
        "text_tertiary": "#6C6C70",
        "accent": "#0A84FF",
        "accent_2": "#5E5CE6",
        "success": "#30D158",
        "warning": "#FF9F0A",
        "error": "#FF453A",
        "gradient_1": "linear-gradient(135deg, #0A84FF, #5E5CE6)",
        "gradient_2": "linear-gradient(135deg, #30D158, #0A84FF)",
    },
    "light": {
        "bg": "#F2F2F7",
        "surface": "rgba(255, 255, 255, 0.95)",
        "surface_2": "rgba(249, 249, 251, 0.95)",
        "border": "rgba(0,0,0,0.08)",
        "text_primary": "#000000",
        "text_secondary": "#6C6C70",
        "text_tertiary": "#8E8E93",
        "accent": "#007AFF",
        "accent_2": "#5856D6",
        "success": "#34C759",
        "warning": "#FF9500",
        "error": "#FF3B30",
        "gradient_1": "linear-gradient(135deg, #007AFF, #5856D6)",
        "gradient_2": "linear-gradient(135deg, #34C759, #007AFF)",
    }
}

def apply_professional_theme():
    c = COLORS[st.session_state.theme]
    
    st.markdown(f"""
    <style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100..900;1,100..900&display=swap');
    
    /* Global reset */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    html, body, .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Main container */
    .main {{
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }}
    
    /* Header */
    .app-header {{
        margin-bottom: 2rem;
        text-align: center;
    }}
    
    .app-header h1 {{
        font-size: 3.5rem;
        font-weight: 700;
        background: {c['gradient_1']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }}
    
    .app-header p {{
        color: {c['text_secondary']};
        font-size: 1rem;
    }}
    
    /* Stats Grid */
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }}
    
    .stat-card {{
        background: {c['surface']};
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid {c['border']};
        transition: all 0.2s ease;
    }}
    
    .stat-card:hover {{
        transform: translateY(-2px);
        background: {c['surface_2']};
    }}
    
    .stat-label {{
        color: {c['text_tertiary']};
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}
    
    .stat-value {{
        color: {c['text_primary']};
        font-size: 2rem;
        font-weight: 700;
    }}
    
    /* Form Cards */
    .form-card {{
        background: {c['surface']};
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid {c['border']};
        margin-bottom: 1.5rem;
    }}
    
    .section-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {c['text_primary']};
        margin-bottom: 1rem;
    }}
    
    /* Activity Grid */
    .activity-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }}
    
    .activity-btn {{
        background: {c['surface_2']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 0.75rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    
    .activity-btn:hover {{
        transform: translateY(-2px);
        background: {c['surface']};
    }}
    
    /* Chat Container */
    .chat-container {{
        background: {c['surface']};
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid {c['border']};
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
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
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        line-height: 1.4;
    }}
    
    .message.user .message-content {{
        background: {c['accent']};
        color: white;
        border-bottom-right-radius: 4px;
    }}
    
    .message.echo .message-content {{
        background: {c['surface_2']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-bottom-left-radius: 4px;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {c['surface']};
        backdrop-filter: blur(10px);
        border-right: 1px solid {c['border']};
    }}
    
    /* Buttons */
    .stButton button {{
        background: {c['surface_2']};
        border: 1px solid {c['border']};
        border-radius: 30px;
        color: {c['text_primary']};
        transition: all 0.2s ease;
    }}
    
    .stButton button:hover {{
        background: {c['accent']};
        border-color: {c['accent']};
        transform: translateY(-1px);
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {c['surface_2']};
        border-radius: 3px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {c['accent']};
        border-radius: 3px;
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# Apply themes
apply_dynamic_background()
apply_professional_theme()

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
        st.session_state.chat_history = []
        st.session_state.sarcasm_mode = True
        
        new_badges = st.session_state.gamification.check_and_award_badges()
        if new_badges:
            st.session_state.new_badges = new_badges

c = COLORS[st.session_state.theme]

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem 0;">
        <div style="font-size: 3rem;">🧠</div>
        <h2 style="margin: 0.5rem 0 0; color: {c['text_primary']};">ECHO</h2>
        <p style="color: {c['text_tertiary']}; font-size: 0.75rem;">Personal AI Memory</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Theme toggle
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
    
    # Background Gallery
    with st.expander("🎨 Background Gallery", expanded=False):
        st.markdown("**Quick Backgrounds**")
        
        # Quick backgrounds grid
        quick_bgs = [
            ("🌙 Midnight", "gradient_dark"),
            ("🌅 Sunrise", "gradient_light"),
            ("🌲 Forest", "forest"),
            ("🌊 Ocean", "ocean"),
            ("🌇 Sunset", "sunset"),
            ("🌸 Cherry", "cherry"),
            ("✨ Aurora", "aurora"),
            ("☕ Coffee", "coffee"),
            ("🎮 Neon", "neon")
        ]
        
        for i, (name, bg_key) in enumerate(quick_bgs):
            if st.button(name, use_container_width=True, key=f"bg_{bg_key}"):
                st.session_state.background_style = bg_key
                save_background_preference()
                st.rerun()
        
        st.markdown("---")
        st.markdown("**✨ Aesthetic Presets**")
        
        # Aesthetic backgrounds
        for name, url in list(AESTHETIC_BACKGROUNDS.items())[:5]:
            if st.button(name, use_container_width=True, key=f"ast_{name}"):
                st.session_state.background_style = "custom"
                st.session_state.custom_bg_url = url
                save_background_preference()
                st.rerun()
        
        st.markdown("---")
        st.markdown("**🖼️ Custom Image**")
        custom_url = st.text_input("Image URL", placeholder="https://images.unsplash.com/...")
        if st.button("Apply Custom", use_container_width=True):
            if custom_url:
                st.session_state.background_style = "custom"
                st.session_state.custom_bg_url = custom_url
                save_background_preference()
                st.rerun()
        
        st.caption("💡 Find images on Unsplash, Pexels, or Pixabay")
    
    st.markdown("---")
    
    # Stats
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
    
    # Personality selector
    st.markdown(f"<p style='color: {c['text_secondary']}; font-size: 0.75rem; margin-bottom: 0.5rem;'>PERSONALITY</p>", unsafe_allow_html=True)
    
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
    
    # Sarcasm mode
    st.session_state.sarcasm_mode = st.toggle(
        "🎭 Sarcasm Mode", 
        value=st.session_state.sarcasm_mode,
        help="When enabled, ECHO responds with personality"
    )
    
    # Update memories button
    if st.button("🔄 Sync Memories", use_container_width=True):
        with st.spinner("Analyzing patterns..."):
            new_insights = st.session_state.memory_engine.update_memories()
            if new_insights.get('new_insights'):
                st.success(f"✨ {len(new_insights['new_insights'])} new insights!")

# ============================================
# MAIN CONTENT
# ============================================

st.markdown(f"""
<div class="app-header">
    <h1>ECHO</h1>
    <p>Your personal AI memory system</p>
</div>
""", unsafe_allow_html=True)

# Stats Grid
stats = st.session_state.gamification.get_statistics()
summary = st.session_state.event_logger.get_event_summary(days=7)

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-label">Total Events</div>
        <div class="stat-value">{stats['total_events']}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">This Week</div>
        <div class="stat-value">{summary['total_events']}</div>
        <div class="stat-label" style="margin-top: 0.5rem;">{summary['unique_days']} active days</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Current Level</div>
        <div class="stat-value">{stats['level']}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Badges</div>
        <div class="stat-value">{stats['badges_earned']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Actions
st.markdown(f"""
<div class="form-card">
    <div class="section-title">⚡ Quick Log</div>
    <div class="activity-grid">
        <div class="activity-btn" onclick="alert('Quick log feature - use the form below')">
            <div class="activity-icon">💻</div>
            <div class="activity-name">Coding</div>
        </div>
        <div class="activity-btn" onclick="alert('Quick log feature - use the form below')">
            <div class="activity-icon">📝</div>
            <div class="activity-name">Note</div>
        </div>
        <div class="activity-btn" onclick="alert('Quick log feature - use the form below')">
            <div class="activity-icon">✅</div>
            <div class="activity-name">Task</div>
        </div>
        <div class="activity-btn" onclick="alert('Quick log feature - use the form below')">
            <div class="activity-icon">📚</div>
            <div class="activity-name">Learn</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_titles = ["📝 Log Activity", "💭 Reflections", "📊 Insights", "💬 Chat", "🏆 Profile"]
tabs = st.tabs(tab_titles)

# ============================================
# TAB 1: LOG ACTIVITY
# ============================================

with tabs[0]:
    st.markdown(f"""
    <div class="form-card">
        <div class="section-title">Log Your Activity</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("log_form"):
            event_type = st.selectbox(
                "Activity Type",
                ["coding", "note", "task", "meeting", "learning", "exercise", "other"],
                format_func=lambda x: f"📌 {x.title()}"
            )
            content = st.text_area("What are you doing?", placeholder="Describe your activity...")
            duration = st.slider("Duration (minutes)", 5, 240, 30)
            tags = st.text_input("Tags", placeholder="work, focus, important")
            
            if st.form_submit_button("Save Activity", use_container_width=True):
                if content:
                    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
                    st.session_state.event_logger.log_event(event_type, content, duration, tags_list)
                    st.success("✓ Activity saved!")
                    st.balloons()
                    time.sleep(0.5)
                    st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">Recent</div>
        </div>
        """, unsafe_allow_html=True)
        recent = st.session_state.event_logger.get_events(limit=3)
        if not recent.empty:
            for _, row in recent.iterrows():
                st.markdown(f"""
                <div style="background: {c['surface_2']}; border-radius: 12px; padding: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="color: {c['text_tertiary']}; font-size: 0.7rem;">{row['timestamp'].strftime('%I:%M %p')}</div>
                    <div style="color: {c['text_primary']}; font-size: 0.875rem;">{row['content'][:60]}</div>
                    <div style="color: {c['text_tertiary']}; font-size: 0.7rem;">⏱️ {row['duration_minutes']} min</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activities yet. Log your first one above!")

# ============================================
# TAB 2: REFLECTIONS
# ============================================

with tabs[1]:
    st.markdown(f"""
    <div class="form-card">
        <div class="section-title">AI Reflections</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        focus = st.selectbox("Focus Area", ["General", "Productivity", "Consistency", "Patterns"])
        if st.button("✨ Generate Reflection", use_container_width=True):
            with st.spinner("ECHO is thinking..."):
                reflection = st.session_state.ai_reflection.generate_reflection(focus.lower())
                st.session_state.current_reflection = reflection
    
    with col2:
        if 'current_reflection' in st.session_state:
            st.markdown(f"""
            <div style="background: {c['surface_2']}; border-radius: 16px; padding: 1rem; border-left: 3px solid {c['accent']};">
                <div style="color: {c['text_primary']}; font-size: 0.95rem; line-height: 1.5;">
                    {st.session_state.current_reflection}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# TAB 3: INSIGHTS
# ============================================

with tabs[2]:
    patterns = st.session_state.memory_engine.user_profile.get("behavioral_patterns", {})
    
    if patterns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="form-card">
                <div class="section-title">⏰ Peak Hours</div>
            </div>
            """, unsafe_allow_html=True)
            hourly = patterns.get("hourly", {})
            if hourly.get("peak_hours"):
                for hour in hourly['peak_hours'][:3]:
                    st.markdown(f"""
                    <div style="background: {c['surface_2']}; border-radius: 12px; padding: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.25rem; font-weight: 600; color: {c['accent']};">{hour}:00</div>
                        <div style="color: {c['text_tertiary']}; font-size: 0.75rem;">Peak productivity hour</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="form-card">
                <div class="section-title">📅 Best Day</div>
            </div>
            """, unsafe_allow_html=True)
            weekly = patterns.get("weekly", {})
            if weekly.get("most_productive_day"):
                st.markdown(f"""
                <div style="background: {c['surface_2']}; border-radius: 12px; padding: 0.75rem; text-align: center;">
                    <div style="font-size: 2rem;">⭐</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {c['text_primary']};">{weekly['most_productive_day']}</div>
                    <div style="color: {c['text_tertiary']}; font-size: 0.75rem;">Your most productive day</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📊 Log more activities to see insights about your patterns!")

# ============================================
# TAB 4: CHAT
# ============================================

with tabs[3]:
    current = st.session_state.query_interface.personality_manager.get_personality_info()
    
    st.markdown(f"""
    <div class="chat-container">
    """, unsafe_allow_html=True)
    
    for role, message in st.session_state.chat_history[-15:]:
        if role == "user":
            st.markdown(f"""
            <div class="message user">
                <div class="message-content">{message}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message echo">
                <div class="message-content">{message}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f"""
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("", placeholder=f"Ask {current['name']} anything...", key="chat_input", label_visibility="collapsed")
    with col2:
        send_button = st.button("Send", use_container_width=True, key="send_button")
    
    if send_button and user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner(f"{current['details']['icon']} {current['name']} is thinking..."):
            response = st.session_state.query_interface.answer_query_with_personality(user_input)
        st.rerun()

# ============================================
# TAB 5: PROFILE
# ============================================

with tabs[4]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">🏆 Badges</div>
        </div>
        """, unsafe_allow_html=True)
        
        earned = st.session_state.gamification.get_earned_badges()
        if earned:
            for badge in earned:
                st.markdown(f"""
                <div style="background: {c['surface_2']}; border-radius: 12px; padding: 0.75rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem;">
                    <div style="font-size: 1.5rem;">🏅</div>
                    <div>
                        <div style="color: {c['text_primary']}; font-weight: 500;">{badge['name']}</div>
                        <div style="color: {c['text_tertiary']}; font-size: 0.7rem;">{badge['description']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Complete activities to earn badges!")
    
    with col2:
        st.markdown(f"""
        <div class="form-card">
            <div class="section-title">📊 Progress</div>
        </div>
        """, unsafe_allow_html=True)
        
        level_info = st.session_state.gamification.get_level()
        st.progress(level_info['progress'] / 100, text=f"Level {level_info['current_level']} → {level_info['current_level'] + 1}")
        
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: {c['text_secondary']};">Total Events</span>
                <span style="color: {c['text_primary']};">{stats['total_events']}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: {c['text_secondary']};">Current Streak</span>
                <span style="color: {c['text_primary']};">{stats['streak']} days</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================

st.markdown(f"""
<div style="text-align: center; padding: 2rem 0 1rem; color: {c['text_tertiary']}; font-size: 0.75rem;">
    ECHO — Personal AI Memory System
</div>
""", unsafe_allow_html=True)