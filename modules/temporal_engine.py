# modules/temporal_engine.py
"""
Temporal analysis engine for detecting behavioral patterns across time windows.
Uses pandas for time series analysis and pattern detection.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class TemporalEngine:
    def __init__(self, event_logger):
        """Initialize with reference to event logger."""
        self.event_logger = event_logger
    
    def analyze_hourly_patterns(self, days: int = 30) -> Dict:
        """
        Detect peak productivity hours and activity patterns.
        
        Returns:
            Dictionary with hourly activity analysis
        """
        start_date = datetime.now() - timedelta(days=days)
        df = self.event_logger.get_events(start_date=start_date)
        
        if df.empty:
            return {"peak_hours": [], "activity_distribution": {}}
        
        # Calculate activity by hour
        hourly_activity = df.groupby('hour').size()
        
        # Find peak hours (top 3)
        peak_hours = hourly_activity.nlargest(3).index.tolist()
        
        # Calculate rolling average for trend detection
        df_sorted = df.sort_values('timestamp')
        df_sorted['rolling_activity'] = df_sorted.groupby(df_sorted['timestamp'].dt.date).cumcount()
        
        return {
            "peak_hours": peak_hours,
            "peak_hour_intensity": hourly_activity.max(),
            "activity_distribution": hourly_activity.to_dict(),
            "most_active_hour": int(hourly_activity.idxmax()) if not hourly_activity.empty else None,
            "least_active_hour": int(hourly_activity.idxmin()) if not hourly_activity.empty else None
        }
    
    def detect_weekly_patterns(self, weeks: int = 8) -> Dict:
        """
        Analyze weekly patterns including consistency and drop-offs.
        
        Returns:
            Dictionary with weekly pattern analysis
        """
        start_date = datetime.now() - timedelta(weeks=weeks)
        df = self.event_logger.get_events(start_date=start_date)
        
        if df.empty:
            return {"consistency_score": 0, "trend": "insufficient_data"}
        
        # Group by week and day
        df['week'] = df['timestamp'].dt.isocalendar().week
        df['weekday'] = df['timestamp'].dt.day_name()
        
        weekly_activity = df.groupby(['week', 'weekday']).size().unstack(fill_value=0)
        
        # Calculate consistency (standard deviation across weeks)
        consistency_score = 1 - (weekly_activity.std().mean() / (weekly_activity.mean().mean() + 1))
        
        # Detect drop-offs (weeks with significantly lower activity)
        weekly_totals = df.groupby('week').size()
        avg_weekly = weekly_totals.mean()
        drop_off_weeks = weekly_totals[weekly_totals < avg_weekly * 0.5].index.tolist()
        
        # Trend detection using linear regression
        if len(weekly_totals) > 3:
            weeks_num = np.arange(len(weekly_totals))
            z = np.polyfit(weeks_num, weekly_totals.values, 1)
            trend = "increasing" if z[0] > 0 else "decreasing" if z[0] < 0 else "stable"
            trend_strength = abs(z[0]) / (weekly_totals.mean() + 1)
        else:
            trend = "insufficient_data"
            trend_strength = 0
        
        # Find most and least productive days
        daily_avg = df.groupby('weekday').size()
        most_productive_day = daily_avg.idxmax() if not daily_avg.empty else None
        least_productive_day = daily_avg.idxmin() if not daily_avg.empty else None
        
        return {
            "consistency_score": round(consistency_score, 3),
            "drop_off_weeks": drop_off_weeks,
            "trend": trend,
            "trend_strength": round(trend_strength, 3),
            "most_productive_day": most_productive_day,
            "least_productive_day": least_productive_day,
            "weekly_averages": weekly_totals.to_dict(),
            "daily_averages": daily_avg.to_dict()
        }
    
    def detect_bursts_and_lulls(self, window_hours: int = 24, threshold_percentile: int = 80) -> Dict:
        """
        Detect activity bursts (high intensity periods) and lulls (inactivity periods).
        
        Returns:
            Dictionary with burst and lull patterns
        """
        df = self.event_logger.get_events(start_date=datetime.now() - timedelta(days=30))
        
        if df.empty:
            return {"bursts": [], "lulls": []}
        
        # Create time-indexed activity count
        df.set_index('timestamp', inplace=True)
        hourly_counts = df.resample('1h').size()
        
        # Detect bursts (hours above threshold)
        threshold = np.percentile(hourly_counts, threshold_percentile)
        burst_hours = hourly_counts[hourly_counts >= threshold].index
        
        # Detect lulls (consecutive hours with zero activity)
        lull_periods = []
        current_lull = []
        
        for i, (timestamp, count) in enumerate(hourly_counts.items()):
            if count == 0:
                current_lull.append(timestamp)
            elif current_lull:
                if len(current_lull) >= 4:  # 4+ hours of inactivity
                    lull_periods.append({
                        "start": current_lull[0],
                        "end": current_lull[-1],
                        "duration_hours": len(current_lull)
                    })
                current_lull = []
        
        return {
            "bursts": [
                {
                    "time": ts,
                    "activity_count": int(hourly_counts[ts])
                }
                for ts in burst_hours[:10]  # Top 10 burst hours
            ],
            "lulls": lull_periods[:5],  # Top 5 lull periods
            "avg_hourly_activity": float(hourly_counts.mean()),
            "peak_hourly_activity": int(hourly_counts.max())
        }
    
    def calculate_rolling_metrics(self, window_days: int = 7) -> pd.DataFrame:
        """
        Calculate rolling averages for trend visualization.
        
        Returns:
            DataFrame with rolling metrics
        """
        df = self.event_logger.get_events(start_date=datetime.now() - timedelta(days=90))
        
        if df.empty:
            return pd.DataFrame()
        
        # Daily aggregation
        daily_activity = df.groupby('date').size().reset_index(name='count')
        daily_activity['date'] = pd.to_datetime(daily_activity['date'])
        daily_activity = daily_activity.set_index('date')
        
        # Calculate rolling metrics
        daily_activity['rolling_7d'] = daily_activity['count'].rolling(window=window_days).mean()
        daily_activity['rolling_30d'] = daily_activity['count'].rolling(window=30).mean()
        
        # Calculate percentage change
        daily_activity['pct_change'] = daily_activity['count'].pct_change() * 100
        
        return daily_activity