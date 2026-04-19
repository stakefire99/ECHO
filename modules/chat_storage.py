# modules/chat_storage.py
"""
Chat history storage with 24-hour retention
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Tuple

class ChatStorage:
    def __init__(self, storage_file="data/chat_history.json"):
        self.storage_file = storage_file
        self.ensure_storage_exists()
    
    def ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        if not os.path.exists("data"):
            os.makedirs("data")
        
        if not os.path.exists(self.storage_file):
            self.save_history([])
    
    def save_history(self, history: List[Tuple[str, str, str]]):
        """Save chat history with timestamps"""
        # Each entry: (role, message, timestamp)
        with open(self.storage_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def load_history(self) -> List[Tuple[str, str, str]]:
        """Load chat history"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def add_message(self, role: str, message: str):
        """Add a new message with current timestamp"""
        history = self.load_history()
        timestamp = datetime.now().isoformat()
        history.append([role, message, timestamp])
        self.save_history(history)
    
    def get_today_messages(self) -> List[Tuple[str, str]]:
        """Get only today's messages (last 24 hours)"""
        history = self.load_history()
        now = datetime.now()
        today_messages = []
        
        for role, message, timestamp_str in history:
            msg_time = datetime.fromisoformat(timestamp_str)
            # Check if message is from last 24 hours
            if now - msg_time < timedelta(hours=24):
                today_messages.append((role, message))
        
        return today_messages
    
    def clear_old_messages(self):
        """Remove messages older than 24 hours"""
        history = self.load_history()
        now = datetime.now()
        
        # Keep only messages from last 24 hours
        fresh_history = []
        for role, message, timestamp_str in history:
            msg_time = datetime.fromisoformat(timestamp_str)
            if now - msg_time < timedelta(hours=24):
                fresh_history.append([role, message, timestamp_str])
        
        self.save_history(fresh_history)
        return len(history) - len(fresh_history)  # Number of messages removed
    
    def get_message_count_today(self) -> int:
        """Get number of messages from today"""
        return len(self.get_today_messages())
    
    def get_oldest_message_time(self):
        """Get timestamp of oldest message in storage"""
        history = self.load_history()
        if not history:
            return None
        
        oldest = min(datetime.fromisoformat(msg[2]) for msg in history)
        return oldest
    
    def get_newest_message_time(self):
        """Get timestamp of newest message in storage"""
        history = self.load_history()
        if not history:
            return None
        
        newest = max(datetime.fromisoformat(msg[2]) for msg in history)
        return newest