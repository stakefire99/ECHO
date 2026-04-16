# modules/ai_reflection.py
"""
AI reflection layer that converts structured insights into natural language.
Uses LLM to generate personalized, context-aware reflections.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

# Try to import OpenAI with better error handling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"Note: OpenAI library not available. Using template-based reflections. Error: {e}")
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"Note: Could not initialize OpenAI. Using template-based reflections. Error: {e}")

class AIReflection:
    def __init__(self, memory_engine, api_key: Optional[str] = None):
        """Initialize AI reflection engine."""
        self.memory_engine = memory_engine
        self.use_openai = False
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE:
            try:
                # Try to get API key from parameter or environment
                api_key = api_key or os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    self.use_openai = True
                    print("✓ OpenAI client initialized successfully")
                else:
                    print("ℹ️ OpenAI API key not found. Using template-based reflections.")
            except Exception as e:
                print(f"⚠️ Could not initialize OpenAI client: {e}")
                self.use_openai = False
        else:
            print("ℹ️ OpenAI library not installed. Using template-based reflections.")
    
    def generate_reflection(self, focus: str = "general") -> str:
        """
        Generate a natural language reflection based on user data.
        
        Args:
            focus: Area to focus on ('general', 'productivity', 'consistency', 'patterns')
        
        Returns:
            Natural language reflection string
        """
        # Gather relevant data
        insights = self.memory_engine.user_profile.get("behavioral_patterns", {})
        structured_insights = self.memory_engine._generate_structured_insights()
        
        if self.use_openai:
            return self._generate_llm_reflection(insights, structured_insights, focus)
        else:
            return self._generate_template_reflection(insights, structured_insights, focus)
    
    def _generate_llm_reflection(self, insights: Dict, structured_insights: List[Dict], focus: str) -> str:
        """Generate reflection using OpenAI API."""
        
        # Prepare context for LLM
        context = self._prepare_llm_context(insights, structured_insights, focus)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are ECHO, a personal AI memory system that provides meaningful, 
                        data-driven reflections about user behavior. Your responses should be:
                        1. Based strictly on the provided data
                        2. Personal and conversational in tone
                        3. Insightful without being generic
                        4. Focused on patterns and changes over time
                        5. Encouraging but honest about patterns
                        6. Keep responses to 2-3 sentences"""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            reflection = response.choices[0].message.content.strip()
            
            # Store the generated insight
            self._store_reflection(reflection, structured_insights)
            
            return reflection
            
        except Exception as e:
            print(f"Error generating LLM reflection: {e}")
            return self._generate_template_reflection(insights, structured_insights, focus)
    
    def _prepare_llm_context(self, insights: Dict, structured_insights: List[Dict], focus: str) -> str:
        """Prepare context string for LLM."""
        context = f"Generate a personal reflection about {focus} based on this user data:\n\n"
        
        # Add hourly patterns
        hourly = insights.get("hourly", {})
        if hourly.get("peak_hours"):
            context += f"Peak activity hours: {hourly['peak_hours']}\n"
        if hourly.get("most_active_hour"):
            context += f"Most active hour: {hourly['most_active_hour']}:00\n"
        
        # Add weekly patterns
        weekly = insights.get("weekly", {})
        if weekly.get("most_productive_day"):
            context += f"Most productive day: {weekly['most_productive_day']}\n"
        if weekly.get("least_productive_day"):
            context += f"Least productive day: {weekly['least_productive_day']}\n"
        if weekly.get("consistency_score"):
            context += f"Consistency score (0-1, higher is more consistent): {weekly['consistency_score']}\n"
        if weekly.get("trend"):
            context += f"Overall activity trend: {weekly['trend']}\n"
        
        # Add burst/lull patterns
        burst_lull = insights.get("burst_lull", {})
        if burst_lull.get("peak_hourly_activity"):
            context += f"Peak hourly activity: {burst_lull['peak_hourly_activity']} events\n"
        if burst_lull.get("avg_hourly_activity"):
            context += f"Average hourly activity: {burst_lull['avg_hourly_activity']:.1f} events\n"
        
        # Add structured insights
        if structured_insights:
            context += "\nKey behavioral insights:\n"
            for insight in structured_insights[:3]:
                context += f"- {insight['insight']}\n"
        
        context += "\nGenerate a thoughtful, personalized reflection (2-3 sentences) based on this data. Be specific and mention actual numbers where relevant."
        
        return context
    
    def _generate_template_reflection(self, insights: Dict, structured_insights: List[Dict], focus: str) -> str:
        """Generate reflection using templates when LLM is not available."""
        
        if not structured_insights and not insights.get("hourly", {}).get("peak_hours"):
            return "📝 Not enough data yet to generate meaningful reflections. Keep logging your activities - I'm learning your patterns!"
        
        # Build reflection from available insights
        reflection_parts = []
        
        # Add time-based insight
        hourly = insights.get("hourly", {})
        if hourly.get("peak_hours"):
            peak_hours_str = ", ".join([f"{h}:00" for h in hourly["peak_hours"][:2]])
            reflection_parts.append(f"🎯 You're most active between {peak_hours_str}")
        
        # Add trend insight
        weekly = insights.get("weekly", {})
        if weekly.get("trend") == "increasing":
            trend_strength = weekly.get("trend_strength", 0)
            if trend_strength > 0.1:
                reflection_parts.append(f"📈 Your activity has been trending upward (↑{trend_strength:.0%} week over week)")
            else:
                reflection_parts.append("📈 Your activity has been showing positive momentum")
        elif weekly.get("trend") == "decreasing":
            trend_strength = weekly.get("trend_strength", 0)
            if trend_strength > 0.1:
                reflection_parts.append(f"📉 Your activity has been decreasing (↓{trend_strength:.0%} week over week)")
            else:
                reflection_parts.append("📉 Your activity has been slowly declining")
        
        # Add consistency insight
        if weekly.get("consistency_score", 0) > 0.7:
            reflection_parts.append("✨ You're remarkably consistent in your daily patterns")
        elif weekly.get("consistency_score", 1) < 0.3:
            reflection_parts.append("🎲 Your daily activity varies quite a bit")
        
        # Add burst insight
        burst_lull = insights.get("burst_lull", {})
        if burst_lull.get("bursts"):
            peak = burst_lull.get('peak_hourly_activity', 0)
            reflection_parts.append(f"⚡ You have intense activity bursts (up to {peak} events/hour)")
        
        # Add day-specific insight
        if weekly.get("most_productive_day"):
            reflection_parts.append(f"🌟 {weekly['most_productive_day']} is your most productive day")
        
        # Combine into coherent reflection
        if reflection_parts:
            # Start with a personalized greeting based on time of day
            current_hour = datetime.now().hour
            if current_hour < 12:
                greeting = "Good morning! "
            elif current_hour < 18:
                greeting = "Good afternoon! "
            else:
                greeting = "Good evening! "
            
            reflection = greeting + ". ".join(reflection_parts) + "."
            
            # Add a personalized follow-up based on focus
            if focus == "productivity" and weekly.get("most_productive_day"):
                reflection += f" Consider scheduling important tasks on {weekly['most_productive_day']}s."
            elif focus == "consistency" and weekly.get("consistency_score", 0) < 0.5:
                reflection += " Establishing more consistent routines might help with your goals."
            elif focus == "patterns" and hourly.get("peak_hours"):
                first_peak = hourly["peak_hours"][0] if hourly["peak_hours"] else None
                if first_peak:
                    reflection += f" Your energy peaks around {first_peak}:00 - great time for focused work."
        else:
            reflection = "🎯 Keep logging your activities! I'm building a picture of your patterns and will share insights soon."
        
        # Store the generated insight
        self._store_reflection(reflection, structured_insights)
        
        return reflection
    
    def _store_reflection(self, reflection: str, insights: List[Dict]):
        """Store generated reflection in memory engine."""
        if "insights_generated" not in self.memory_engine.user_profile:
            self.memory_engine.user_profile["insights_generated"] = []
        
        self.memory_engine.user_profile["insights_generated"].append({
            "timestamp": datetime.now().isoformat(),
            "reflection": reflection,
            "related_insights": [i["type"] for i in insights[:3]]
        })
        
        # Keep only last 50 insights
        if len(self.memory_engine.user_profile["insights_generated"]) > 50:
            self.memory_engine.user_profile["insights_generated"] = self.memory_engine.user_profile["insights_generated"][-50:]
        
        self.memory_engine._save_profile()
    
    def generate_weekly_summary(self) -> str:
        """Generate a weekly summary reflection."""
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get events from last week
        df = self.memory_engine.event_logger.get_events(start_date=week_ago)
        
        if df.empty:
            return "No activities logged this week. Start logging to get weekly insights!"
        
        # Calculate weekly stats
        total_events = len(df)
        unique_days = df['date'].nunique()
        avg_per_day = total_events / max(unique_days, 1)
        
        # Get most common event type
        top_event = df['event_type'].mode().iloc[0] if not df.empty else None
        
        # Get previous week for comparison
        two_weeks_ago = datetime.now() - timedelta(days=14)
        prev_df = self.memory_engine.event_logger.get_events(
            start_date=two_weeks_ago,
            end_date=week_ago
        )
        
        summary = f"📊 **Weekly Summary**\n\n"
        summary += f"You logged {total_events} activities across {unique_days} days "
        summary += f"(avg {avg_per_day:.1f} per active day).\n"
        
        if top_event:
            summary += f"Your most common activity type was '{top_event}'.\n"
        
        # Add comparison with previous week
        if not prev_df.empty:
            prev_total = len(prev_df)
            change = ((total_events - prev_total) / prev_total) * 100
            if change > 10:
                summary += f"\n🎉 {change:.0f}% more active than last week! Great momentum!"
            elif change < -10:
                summary += f"\n📉 {abs(change):.0f}% less active than last week. Ready for a fresh start?"
            else:
                summary += f"\n✓ Activity levels similar to last week ({change:.0f}% change). Steady progress!"
        
        return summary
    
    def generate_motivational_reflection(self) -> str:
        """Generate a motivational reflection based on long-term patterns."""
        insights = self.memory_engine.user_profile.get("behavioral_patterns", {})
        weekly = insights.get("weekly", {})
        
        # Check for streaks or improvements
        if weekly.get("trend") == "increasing":
            return "🌟 You're building momentum! Your consistency is creating positive habits. Keep going!"
        elif weekly.get("trend") == "decreasing":
            return "💪 Every day is a new opportunity. Small steps today can rebuild your momentum - you've got this!"
        elif weekly.get("consistency_score", 0) > 0.7:
            return "🎯 Your consistency is your superpower! Those small daily actions add up to big results."
        else:
            return "✨ Progress isn't always linear. The important thing is that you're showing up and tracking your journey!"