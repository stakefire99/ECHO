# modules/personalities.py
"""
ECHO Personality System - Different tones for different moods
"""

import random
from typing import Dict, List

class PersonalityManager:
    def __init__(self):
        self.current_personality = "mentor"  # default
        self.user_selected_name = "ECHO"
        
        # Define all personalities
        self.personalities = {
            "mentor": {
                "name": "The Mentor",
                "icon": "🎓",
                "description": "Wise, guiding, pushes you to be better",
                "greetings": [
                    "Let's review your progress today.",
                    "I've been analyzing your patterns. Ready for insights?",
                    "Growth comes from reflection. Shall we begin?"
                ],
                "tone_indicators": ["I notice", "Based on patterns", "Consider this", "Growth opportunity"],
                "response_style": "Wise, analytical, slightly formal but caring"
            },
            "friend": {
                "name": "The Friend",
                "icon": "👋",
                "description": "Casual, supportive, like a buddy",
                "greetings": [
                    "Hey! How's it going?",
                    "Yo! Checked out your week yet?",
                    "What's up? Wanna see how you've been doing?"
                ],
                "tone_indicators": ["Hey,", "So...", "You know what's cool?", "Honestly,"],
                "response_style": "Casual, encouraging, uses contractions, friendly"
            },
            "well_wisher": {
                "name": "The Well-Wisher",
                "icon": "💝",
                "description": "Gentle, compassionate, celebrates your wins",
                "greetings": [
                    "I'm so proud of your journey!",
                    "Ready to see how amazing you've been?",
                    "You're doing wonderfully. Shall we reflect together?"
                ],
                "tone_indicators": ["I'm so proud", "That's wonderful", "You should feel good about", "Remember to be kind to yourself"],
                "response_style": "Gentle, nurturing, celebrates small wins, emotionally supportive"
            },
            "sarcastic": {
                "name": "The Sarcastic One",
                "icon": "🎭",
                "description": "Witty, funny, keeps you humble",
                "greetings": [
                    "Oh good, you're back. I was getting lonely judging your absence.",
                    "Finally! I've been waiting. Do you know how boring silence is?",
                    "Well, well, well... look who decided to check in."
                ],
                "tone_indicators": ["Oh wow,", "Well, well,", "Congratulations on the bare minimum,", "I'm shocked, shocked I tell you,"],
                "response_style": "Witty, sarcastic, playful jabs, but still caring underneath"
            }
        }
    
    def set_personality(self, personality_id: str):
        """Change ECHO's personality"""
        if personality_id in self.personalities:
            self.current_personality = personality_id
            return True
        return False
    
    def set_name(self, name: str):
        """Let user rename ECHO"""
        self.user_selected_name = name
        return f"✓ I'll now respond to '{name}'"
    
    def get_greeting(self) -> str:
        """Get a greeting based on current personality"""
        return random.choice(self.personalities[self.current_personality]["greetings"])
    
    def get_response_prefix(self) -> str:
        """Get a tone indicator for the response"""
        return random.choice(self.personalities[self.current_personality]["tone_indicators"])
    
    def transform_response(self, original_response: str, context: str = "general") -> str:
        """Transform a standard response into personality-specific response"""
        personality = self.personalities[self.current_personality]
        
        # Add personality prefix
        prefix = self.get_response_prefix()
        
        # Transform based on personality
        if self.current_personality == "mentor":
            # Make it more analytical
            response = f"{prefix} {original_response.lower()}"
            response = response.replace("you were", "your pattern shows")
            response = response.replace("you are", "you appear to be")
            
        elif self.current_personality == "friend":
            # Make it more casual
            response = f"{prefix} {original_response.lower()}"
            response = response.replace(" productivity ", " getting stuff done ")
            response = response.replace(" activities ", " things ")
            
        elif self.current_personality == "well_wisher":
            # Add encouragement
            response = f"{prefix} {original_response.lower()}"
            if "good" in original_response.lower() or "increase" in original_response.lower():
                response += " That's genuinely wonderful!"
            elif "decrease" in original_response.lower() or "low" in original_response.lower():
                response += " Remember, every day is a fresh start. You've got this!"
                
        elif self.current_personality == "sarcastic":
            # Keep the existing sarcasm (already handled in query_interface)
            response = original_response
            
        # Add signature based on personality
        signatures = {
            "mentor": ["\n\n*Reflect on this.*", "\n\n*Growth is a journey.*"],
            "friend": ["\n\n😊 Just saying", "\n\n🤙 Catch you later!"],
            "well_wisher": ["\n\n💝 Sending good energy", "\n\n✨ You're doing amazing"],
            "sarcastic": ["\n\n🤷 Just saying", "\n\n😏 Your welcome."]
        }
        
        if random.random() > 0.7:  # 30% chance of adding signature
            response += random.choice(signatures[self.current_personality])
        
        return response
    
    def get_conversation_log(self, chat_history: List) -> str:
        """Generate a log of past conversations"""
        if not chat_history:
            return "No conversations yet. Start talking with ECHO!"
        
        log = f"🗣️ **Conversation Log with {self.user_selected_name}**\n\n"
        for role, message in chat_history[-20:]:  # Last 20 messages
            if role == "user":
                log += f"**You:** {message}\n"
            else:
                log += f"**{self.user_selected_name}:** {message}\n"
        
        return log
    
    def get_personality_info(self) -> Dict:
        """Get current personality info"""
        return {
            "current": self.current_personality,
            "details": self.personalities[self.current_personality],
            "name": self.user_selected_name
        }