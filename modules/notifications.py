# modules/notifications.py
"""
Push notification system for ECHO
Sends browser notifications for reminders and achievements
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Try to import the push notification component
try:
    from streamlit_push_notifications import send_push
    PUSH_AVAILABLE = True
except ImportError:
    PUSH_AVAILABLE = False
    print("⚠️ streamlit-push-notifications not installed")

class NotificationManager:
    def __init__(self):
        self.notification_history = []
        self.load_history()
    
    def load_history(self):
        """Load notification history from file"""
        try:
            with open("data/notifications.json", "r") as f:
                self.notification_history = json.load(f)
        except FileNotFoundError:
            self.notification_history = []
    
    def save_history(self):
        """Save notification history to file"""
        with open("data/notifications.json", "w") as f:
            json.dump(self.notification_history[-100:], f)  # Keep last 100
    
    def send_browser_notification(self, title, body, icon=None):
        """Send a browser push notification"""
        if not PUSH_AVAILABLE:
            print("Push notifications not available")
            return False
        
        try:
            send_push(
                title=title,
                body=body,
                icon_path=icon or "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/brain_1f9e0.png",
                tag="echo_notification"
            )
            self.notification_history.append({
                "type": "browser",
                "title": title,
                "body": body,
                "timestamp": datetime.now().isoformat()
            })
            self.save_history()
            return True
        except Exception as e:
            print(f"Notification error: {e}")
            return False
    
    def send_in_app_notification(self, message, icon="🔔"):
        """Send an in-app toast notification"""
        st.toast(message, icon=icon)
        self.notification_history.append({
            "type": "in_app",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        self.save_history()
    
    def schedule_daily_reminder(self, hour=20, minute=0):
        """Schedule a daily reminder (runs when app is open)"""
        # This would require a background process
        # For now, just check if it's time
        now = datetime.now()
        if now.hour == hour and now.minute == minute:
            self.send_browser_notification(
                "ECHO Reminder",
                "Time to log your activities for today! 🧠",
                icon="🔔"
            )
    
    def check_for_milestone_notification(self):
        """Check and send notifications for milestones"""
        # Get stats from gamification
        stats = st.session_state.gamification.get_statistics()
        
        # Check for streak milestones
        streak = stats['streak']
        if streak == 7:
            self.send_browser_notification(
                "🏆 Milestone Achieved!",
                f"7-day streak! You're on fire! 🔥",
                icon="🏆"
            )
        elif streak == 30:
            self.send_browser_notification(
                "👑 Legendary Achievement!",
                f"30-day streak! You're a consistency master!",
                icon="👑"
            )
        
        # Check for level up
        level = stats['level']
        if level > st.session_state.get('last_level', 0):
            st.session_state.last_level = level
            self.send_browser_notification(
                "⭐ Level Up!",
                f"Congratulations! You've reached Level {level}!",
                icon="⭐"
            )
    
    def get_notification_history(self):
        """Get all past notifications"""
        return self.notification_history
    
    def clear_history(self):
        """Clear notification history"""
        self.notification_history = []
        self.save_history()