# modules/memory_engine.py
"""
Core memory engine that builds a dynamic user profile and detects meaningful patterns.
Connects past events into evolving insights about user behavior.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Helper function to convert numpy types to Python native types
def convert_to_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {convert_to_serializable(k): convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj

class MemoryEngine:
    def __init__(self, event_logger, temporal_engine):
        """Initialize memory engine with references to other components."""
        self.event_logger = event_logger
        self.temporal_engine = temporal_engine
        self.user_profile = self._load_or_init_profile()
    
    def _load_or_init_profile(self) -> Dict:
        """Load existing user profile or create a new one."""
        profile_path = "data/user_profile.json"
        try:
            with open(profile_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "behavioral_patterns": {},
                "memory_clusters": [],
                "evolution_tracking": [],
                "preferences": {},
                "insights_generated": []
            }
    
    def _save_profile(self):
        """Save user profile to disk with proper JSON serialization."""
        self.user_profile["last_updated"] = datetime.now().isoformat()
        # Convert numpy types to Python native types before saving
        serializable_profile = convert_to_serializable(self.user_profile)
        with open("data/user_profile.json", 'w') as f:
            json.dump(serializable_profile, f, indent=2)
    
    def update_memories(self) -> Dict:
        """
        Main method to update all memories and patterns.
        This should be called periodically to refresh insights.
        
        Returns:
            Dictionary of new insights discovered
        """
        new_insights = []
        
        # Update behavioral patterns
        hourly_patterns = self.temporal_engine.analyze_hourly_patterns()
        weekly_patterns = self.temporal_engine.detect_weekly_patterns()
        burst_lull = self.temporal_engine.detect_bursts_and_lulls()
        
        # Store patterns
        self.user_profile["behavioral_patterns"] = {
            "hourly": hourly_patterns,
            "weekly": weekly_patterns,
            "burst_lull": burst_lull,
            "last_updated": datetime.now().isoformat()
        }
        
        # Detect changes in behavior over time
        evolution = self._detect_behavioral_evolution()
        if evolution:
            new_insights.extend(evolution)
            self.user_profile["evolution_tracking"].append({
                "timestamp": datetime.now().isoformat(),
                "changes": evolution
            })
        
        # Cluster similar events for pattern recognition
        clusters = self._cluster_events_by_similarity()
        self.user_profile["memory_clusters"] = clusters
        
        # Generate meaningful insights from patterns
        insights = self._generate_structured_insights()
        new_insights.extend(insights)
        
        # Update preferences based on behavior
        self._update_preferences()
        
        self._save_profile()
        
        return {
            "new_insights": new_insights,
            "profile_summary": self._get_profile_summary()
        }
    
    def _detect_behavioral_evolution(self) -> List[Dict]:
        """
        Detect how user behavior has changed over time.
        Compares recent behavior with historical patterns.
        """
        insights = []
        
        # Get historical data in chunks
        now = datetime.now()
        last_month = now - timedelta(days=30)
        month_before = now - timedelta(days=60)
        
        recent_df = self.event_logger.get_events(start_date=last_month)
        previous_df = self.event_logger.get_events(
            start_date=month_before,
            end_date=last_month
        )
        
        if recent_df.empty or previous_df.empty:
            return insights
        
        # Compare activity levels
        recent_avg = len(recent_df) / 30
        previous_avg = len(previous_df) / 30
        
        if recent_avg > previous_avg * 1.2:
            insights.append({
                "type": "productivity_increase",
                "severity": "positive",
                "description": f"Activity increased by {((recent_avg/previous_avg - 1) * 100):.0f}% compared to last month",
                "data": {"recent_avg": recent_avg, "previous_avg": previous_avg}
            })
        elif recent_avg < previous_avg * 0.8:
            insights.append({
                "type": "productivity_decrease",
                "severity": "warning",
                "description": f"Activity decreased by {((1 - recent_avg/previous_avg) * 100):.0f}% compared to last month",
                "data": {"recent_avg": recent_avg, "previous_avg": previous_avg}
            })
        
        # Detect changes in peak hours
        if not recent_df.empty:
            recent_peak = recent_df.groupby('hour').size().idxmax()
            if not previous_df.empty:
                previous_peak = previous_df.groupby('hour').size().idxmax()
                if recent_peak != previous_peak:
                    insights.append({
                        "type": "peak_hour_shift",
                        "severity": "info",
                        "description": f"Peak productivity hour shifted from {previous_peak}:00 to {recent_peak}:00",
                        "data": {"previous_peak": previous_peak, "recent_peak": recent_peak}
                    })
        
        return insights
    
    def _cluster_events_by_similarity(self) -> List[Dict]:
        """
        Group similar events together to identify recurring themes.
        Uses tag and content similarity.
        """
        df = self.event_logger.get_events(limit=1000)
        
        if df.empty:
            return []
        
        # Simple clustering based on tags and event types
        clusters = defaultdict(list)
        
        for _, event in df.iterrows():
            # Create cluster key from event type and primary tag
            tags = event['tags'] if isinstance(event['tags'], list) else []
            primary_tag = tags[0] if tags else "uncategorized"
            cluster_key = f"{event['event_type']}:{primary_tag}"
            
            clusters[cluster_key].append({
                "timestamp": event['timestamp'].isoformat(),
                "content": event['content'],
                "duration": event['duration_minutes']
            })
        
        # Convert to list of clusters with metadata
        return [
            {
                "id": i,
                "name": cluster_name,
                "event_count": len(events),
                "first_seen": min(e['timestamp'] for e in events),
                "last_seen": max(e['timestamp'] for e in events),
                "frequency": len(events) / ((datetime.now() - datetime.fromisoformat(min(e['timestamp'] for e in events))).days + 1),
                "events": events[-10:]  # Store only last 10 for context
            }
            for i, (cluster_name, events) in enumerate(clusters.items())
        ]
    
    def _generate_structured_insights(self) -> List[Dict]:
        """
        Generate meaningful insights from detected patterns.
        These are structured insights that can be converted to natural language.
        """
        insights = []
        patterns = self.user_profile.get("behavioral_patterns", {})
        
        # Hourly pattern insights
        hourly = patterns.get("hourly", {})
        if hourly.get("peak_hours"):
            peak_hours_str = ", ".join([f"{h}:00" for h in hourly["peak_hours"][:3]])
            insights.append({
                "type": "peak_hours",
                "confidence": 0.85,
                "insight": f"Most active during {peak_hours_str}",
                "data": {"hours": hourly["peak_hours"]}
            })
        
        # Weekly pattern insights
        weekly = patterns.get("weekly", {})
        if weekly.get("most_productive_day"):
            insights.append({
                "type": "productivity_day",
                "confidence": 0.75,
                "insight": f"Most productive on {weekly['most_productive_day']}s",
                "data": {"day": weekly["most_productive_day"]}
            })
        
        if weekly.get("consistency_score", 0) > 0.7:
            insights.append({
                "type": "consistency",
                "confidence": weekly["consistency_score"],
                "insight": "Very consistent in daily activity patterns",
                "data": {"score": weekly["consistency_score"]}
            })
        elif weekly.get("consistency_score", 1) < 0.3:
            insights.append({
                "type": "inconsistency",
                "confidence": 0.7,
                "insight": "Activity patterns vary significantly day to day",
                "data": {"score": weekly["consistency_score"]}
            })
        
        # Burst and lull insights
        burst_lull = patterns.get("burst_lull", {})
        if burst_lull.get("bursts"):
            insights.append({
                "type": "activity_bursts",
                "confidence": 0.8,
                "insight": f"Experiences high-intensity activity bursts (up to {burst_lull.get('peak_hourly_activity', 0)} events/hour)",
                "data": {"peak_burst": burst_lull.get("peak_hourly_activity")}
            })
        
        if burst_lull.get("lulls"):
            avg_lull_duration = np.mean([l["duration_hours"] for l in burst_lull["lulls"]])
            insights.append({
                "type": "inactivity_periods",
                "confidence": 0.7,
                "insight": f"Typically has {avg_lull_duration:.0f}-hour breaks of inactivity",
                "data": {"avg_lull_hours": avg_lull_duration}
            })
        
        return insights
    
    def _update_preferences(self):
        """Update user preferences based on behavioral patterns."""
        patterns = self.user_profile.get("behavioral_patterns", {})
        
        # Infer preferences from behavior
        hourly = patterns.get("hourly", {})
        if hourly.get("peak_hours"):
            self.user_profile["preferences"]["peak_productivity_hours"] = hourly["peak_hours"]
        
        weekly = patterns.get("weekly", {})
        if weekly.get("most_productive_day"):
            self.user_profile["preferences"]["best_day_for_focus"] = weekly["most_productive_day"]
        
        # Track event type preferences
        df = self.event_logger.get_events(limit=500)
        if not df.empty:
            event_type_counts = df['event_type'].value_counts()
            self.user_profile["preferences"]["preferred_activities"] = event_type_counts.head(5).to_dict()
    
    def _get_profile_summary(self) -> Dict:
        """Get a concise summary of the user profile."""
        patterns = self.user_profile.get("behavioral_patterns", {})
        
        return {
            "profile_age_days": (datetime.now() - datetime.fromisoformat(self.user_profile["created_at"])).days,
            "total_insights_generated": len(self.user_profile.get("insights_generated", [])),
            "active_clusters": len(self.user_profile.get("memory_clusters", [])),
            "recent_insights": self.user_profile.get("insights_generated", [])[-5:],
            "preferences": self.user_profile.get("preferences", {})
        }
    
    def query_memory(self, context: str, time_range: Optional[tuple] = None) -> List[Dict]:
        """
        Query the memory system for relevant memories based on context.
        
        Args:
            context: Query context (e.g., "productivity", "focus", "coding")
            time_range: Optional (start_date, end_date) tuple
        
        Returns:
            List of relevant memories/events
        """
        # Simple keyword-based retrieval for now
        df = self.event_logger.get_events()
        
        if df.empty:
            return []
        
        # Filter by time range if provided
        if time_range:
            start_date, end_date = time_range
            df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
        
        # Search in content and tags
        context_lower = context.lower()
        mask = (
            df['content'].str.lower().str.contains(context_lower, na=False) |
            df['tags'].apply(lambda x: any(context_lower in tag.lower() for tag in x) if x else False)
        )
        
        relevant_events = df[mask].sort_values('timestamp', ascending=False).head(20)
        
        return relevant_events.to_dict('records')
    
    def get_behavioral_trend(self, metric: str, days: int = 30) -> Dict:
        """
        Get trend data for a specific behavioral metric.
        
        Args:
            metric: One of 'activity', 'duration', 'consistency'
            days: Number of days to analyze
        
        Returns:
            Trend analysis including direction and magnitude
        """
        start_date = datetime.now() - timedelta(days=days)
        df = self.event_logger.get_events(start_date=start_date)
        
        if df.empty:
            return {"trend": "insufficient_data", "magnitude": 0}
        
        # Daily aggregation
        daily = df.groupby(df['timestamp'].dt.date).size()
        
        if len(daily) < 7:
            return {"trend": "insufficient_data", "magnitude": 0}
        
        # Calculate trend using linear regression
        x = np.arange(len(daily))
        y = daily.values
        
        slope = np.polyfit(x, y, 1)[0]
        magnitude = slope / (y.mean() + 1)
        
        if abs(magnitude) < 0.05:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "magnitude": round(abs(magnitude), 3),
            "slope": round(slope, 2),
            "current_average": round(y[-7:].mean(), 1) if len(y) >= 7 else round(y.mean(), 1),
            "historical_average": round(y.mean(), 1)
        }