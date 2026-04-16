# modules/event_logger.py
"""
Event logging system for capturing user activities with timestamps.
Stores structured, queryable event data in SQLite.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd

class EventLogger:
    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize the event logger with SQLite database."""
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Create data directory if it doesn't exist."""
        Path("data").mkdir(exist_ok=True)
    
    def _init_database(self):
        """Initialize database schema with optimized indexes for time-based queries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    duration_minutes INTEGER DEFAULT 0,
                    tags TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for fast time-based queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
    
    def log_event(self, 
                  event_type: str, 
                  content: str, 
                  duration_minutes: int = 0,
                  tags: List[str] = None,
                  timestamp: Optional[datetime] = None,
                  metadata: Dict[str, Any] = None) -> int:
        """
        Log a single event to the database.
        
        Args:
            event_type: Type of event (e.g., 'note', 'task', 'coding')
            content: Event content/description
            duration_minutes: Duration of activity in minutes
            tags: List of tags for categorization
            timestamp: Event timestamp (defaults to now)
            metadata: Additional structured data
        
        Returns:
            event_id: The ID of the inserted event
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if tags is None:
            tags = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO events (timestamp, event_type, content, duration_minutes, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                timestamp.isoformat(),
                event_type,
                content,
                duration_minutes,
                json.dumps(tags),
                json.dumps(metadata) if metadata else None
            ))
            return cursor.lastrowid
    
    def log_batch_events(self, events: List[Dict]) -> List[int]:
        """Log multiple events in batch for efficiency."""
        event_ids = []
        for event in events:
            event_id = self.log_event(**event)
            event_ids.append(event_id)
        return event_ids
    
    def get_events(self, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   event_type: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieve events as pandas DataFrame with optional filtering.
        
        Args:
            start_date: Filter events after this date
            end_date: Filter events before this date
            event_type: Filter by event type
            tags: Filter by tags (any match)
            limit: Maximum number of events to return
        
        Returns:
            DataFrame with event data
        """
        query = "SELECT id, timestamp, event_type, content, duration_minutes, tags, metadata FROM events WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if tags:
            # Search for any matching tag in the JSON array
            tag_conditions = " OR ".join(["json_extract(tags, '$') LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f'%"{tag}"%' for tag in tags])
        
        query += " ORDER BY timestamp ASC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)
            
            # Convert timestamp to datetime
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                
                # Parse JSON fields
                df['tags'] = df['tags'].apply(lambda x: json.loads(x) if x else [])
                df['metadata'] = df['metadata'].apply(lambda x: json.loads(x) if x else {})
        
        return df
    
    def get_event_summary(self, days: int = 7) -> Dict:
        """Get summary statistics for recent events."""
        start_date = datetime.now() - pd.Timedelta(days=days)
        df = self.get_events(start_date=start_date)
        
        if df.empty:
            return {"total_events": 0, "event_types": {}, "total_duration": 0}
        
        return {
            "total_events": len(df),
            "event_types": df['event_type'].value_counts().to_dict(),
            "total_duration": df['duration_minutes'].sum(),
            "avg_duration": df['duration_minutes'].mean(),
            "unique_days": df['date'].nunique()
        }