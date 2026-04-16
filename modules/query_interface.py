# modules/query_interface.py
"""
Conversational query interface for ECHO.
Interprets user intent, fetches relevant data, and generates contextual responses.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

class QueryInterface:
    def __init__(self, event_logger, memory_engine, ai_reflection):
        """Initialize the query interface with access to all system components."""
        self.event_logger = event_logger
        self.memory_engine = memory_engine
        self.ai_reflection = ai_reflection
    
    def answer_query(self, query: str) -> str:
        """
        Process a natural language query and return a response.
        
        Args:
            query: User's question about their behavior/patterns
        
        Returns:
            Natural language response
        """
        query_lower = query.lower()
        
        # Detect intent and route to appropriate handler
        if any(word in query_lower for word in ['productive', 'productivity', 'get done', 'accomplish']):
            return self._handle_productivity_query(query_lower)
        
        elif any(word in query_lower for word in ['focus', 'best time', 'peak', 'when do i', 'most active']):
            return self._handle_time_pattern_query(query_lower)
        
        elif any(word in query_lower for word in ['pattern', 'trend', 'change', 'improve', 'decline']):
            return self._handle_pattern_query(query_lower)
        
        elif any(word in query_lower for word in ['week', 'weekly', 'this week', 'last week']):
            return self._handle_weekly_query(query_lower)
        
        elif any(word in query_lower for word in ['consist', 'routine', 'habit']):
            return self._handle_consistency_query(query_lower)
        
        elif any(word in query_lower for word in ['reflect', 'insight', 'summary']):
            return self.ai_reflection.generate_reflection("general")
        
        else:
            return self._handle_general_query(query_lower)
    
    def _handle_productivity_query(self, query: str) -> str:
        """Handle questions about productivity levels."""
        # Get last 7 days of data
        week_ago = datetime.now() - timedelta(days=7)
        df = self.event_logger.get_events(start_date=week_ago)
        
        if df.empty:
            return "I don't have enough data yet to analyze your productivity. Keep logging your activities!"
        
        # Calculate productivity metrics
        total_events = len(df)
        unique_days = df['date'].nunique()
        avg_per_day = total_events / max(unique_days, 1)
        
        # Get today's activity
        today = datetime.now().date()
        today_events = df[df['date'] == today]
        today_count = len(today_events)
        
        # Compare with previous week
        two_weeks_ago = datetime.now() - timedelta(days=14)
        prev_df = self.event_logger.get_events(start_date=two_weeks_ago, end_date=week_ago)
        
        response = f"📊 **Productivity Report (Last 7 days)**\n\n"
        response += f"You logged {total_events} activities across {unique_days} days.\n"
        response += f"Average: {avg_per_day:.1f} activities per active day.\n"
        
        if today_count > 0:
            response += f"Today: {today_count} activities so far.\n"
        
        # Compare with previous week
        if not prev_df.empty:
            prev_total = len(prev_df)
            change = ((total_events - prev_total) / prev_total) * 100
            if change > 10:
                response += f"\n🎉 You've been {change:.0f}% more productive than last week! Great momentum!"
            elif change < -10:
                response += f"\n📉 You've been {abs(change):.0f}% less productive than last week. Ready to turn it around?"
            else:
                response += f"\n✓ Your productivity is stable compared to last week ({change:.0f}% change)."
        
        return response
    
    def _handle_time_pattern_query(self, query: str) -> str:
        """Handle questions about best times for focus/activity."""
        patterns = self.memory_engine.user_profile.get("behavioral_patterns", {})
        hourly = patterns.get("hourly", {})
        
        if not hourly.get("peak_hours"):
            return "I'm still learning your patterns. Log more activities and I'll identify your peak focus hours!"
        
        peak_hours = hourly['peak_hours'][:3]
        peak_hours_str = ", ".join([f"{h}:00" for h in peak_hours])
        
        response = f"⏰ **Your Focus Patterns**\n\n"
        response += f"Your most active hours are: **{peak_hours_str}**\n\n"
        
        if hourly.get('most_active_hour'):
            response += f"Your absolute peak is **{hourly['most_active_hour']}:00** - great time for deep work!\n\n"
        
        if hourly.get('least_active_hour'):
            response += f"You're least active around **{hourly['least_active_hour']}:00** - consider taking breaks or planning low-energy tasks then.\n\n"
        
        response += "💡 *Tip: Schedule your most important tasks during your peak hours for better results!*"
        
        return response
    
    def _handle_pattern_query(self, query: str) -> str:
        """Handle questions about behavioral patterns and trends."""
        # Get trend data
        trend = self.memory_engine.get_behavioral_trend("activity", days=30)
        weekly = self.memory_engine.user_profile.get("behavioral_patterns", {}).get("weekly", {})
        
        response = f"📈 **Behavioral Pattern Analysis**\n\n"
        
        # Trend analysis
        if trend['trend'] == 'increasing':
            response += f"📈 **Trend:** Your activity is **increasing** (↑{trend['magnitude']:.0%} momentum)\n"
            response += f"   Current average: {trend['current_average']:.1f} events/day\n"
        elif trend['trend'] == 'decreasing':
            response += f"📉 **Trend:** Your activity is **decreasing** (↓{trend['magnitude']:.0%} decline)\n"
            response += f"   Current average: {trend['current_average']:.1f} events/day\n"
        else:
            response += f"➡️ **Trend:** Your activity is **stable**\n"
        
        # Weekly patterns
        if weekly.get('most_productive_day'):
            response += f"\n📅 **Best Day:** {weekly['most_productive_day']} is your most productive day\n"
        
        if weekly.get('least_productive_day'):
            response += f"😴 **Challenging Day:** {weekly['least_productive_day']} tends to be less active\n"
        
        # Consistency
        if weekly.get('consistency_score'):
            score = weekly['consistency_score']
            if score > 0.7:
                response += f"\n✨ **Consistency:** Very consistent (score: {score:.0%})\n"
            elif score < 0.3:
                response += f"\n🎲 **Consistency:** Variable patterns (score: {score:.0%})\n"
            else:
                response += f"\n📊 **Consistency:** Moderately consistent (score: {score:.0%})\n"
        
        # Burst patterns
        burst_lull = self.memory_engine.user_profile.get("behavioral_patterns", {}).get("burst_lull", {})
        if burst_lull.get('peak_hourly_activity'):
            response += f"\n⚡ **Work Style:** You show intense focus bursts (up to {burst_lull['peak_hourly_activity']} activities/hour)"
        
        return response
    
    def _handle_weekly_query(self, query: str) -> str:
        """Handle weekly summary queries."""
        return self.ai_reflection.generate_weekly_summary()
    
    def _handle_consistency_query(self, query: str) -> str:
        """Handle questions about consistency and routines."""
        weekly = self.memory_engine.user_profile.get("behavioral_patterns", {}).get("weekly", {})
        
        if not weekly:
            return "I need more data to analyze your consistency patterns. Keep logging your activities!"
        
        score = weekly.get('consistency_score', 0)
        
        response = f"🎯 **Consistency Analysis**\n\n"
        
        if score > 0.7:
            response += f"Excellent! Your consistency score is **{score:.0%}** - you have strong routines!\n\n"
            response += f"Your stable patterns help build momentum and make habits automatic.\n"
        elif score > 0.4:
            response += f"Good! Your consistency score is **{score:.0%}** - you have some routine but room for improvement.\n\n"
            response += f"Try to identify what disrupts your pattern and build small daily habits.\n"
        else:
            response += f"Your consistency score is **{score:.0%}** - your activity varies significantly day to day.\n\n"
            response += f"💡 *Tip: Start with one fixed daily habit at the same time each day to build consistency.*\n"
        
        # Add specific recommendations
        if weekly.get('most_productive_day'):
            response += f"\n📅 You're most consistent on {weekly['most_productive_day']}s - use this as an anchor day!"
        
        return response
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general queries or fallback for unrecognized intents."""
        # Try to find relevant memories
        relevant_memories = self.memory_engine.query_memory(query, time_range=None)
        
        if relevant_memories:
            response = f"Based on your history, I found {len(relevant_memories)} relevant memories:\n\n"
            for memory in relevant_memories[:3]:  # Show top 3
                date = datetime.fromisoformat(memory['timestamp']).strftime('%b %d')
                response += f"• **{date}**: {memory['content'][:100]}\n"
            
            response += f"\nWant to dive deeper into any of these? Just ask!"
            return response
        else:
            return ("I'm not sure how to answer that yet. I can help with questions about:\n"
                   "- Your productivity levels\n"
                   "- Best times for focus\n"
                   "- Behavioral patterns and trends\n"
                   "- Weekly summaries\n"
                   "- Consistency in your routines\n\n"
                   "Try asking something like 'How productive was I this week?' or 'When do I focus best?'")