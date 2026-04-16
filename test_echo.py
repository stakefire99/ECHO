# Test file
# test_echo.py
"""
Test script to verify ECHO is working correctly
"""

from modules import EventLogger, TemporalEngine, MemoryEngine, AIReflection, QueryInterface
from datetime import datetime, timedelta
import random

def test_echo():
    print("🧠 Testing ECHO Personal AI Memory System")
    print("=" * 50)
    
    # Initialize components
    print("\n1. Initializing components...")
    event_logger = EventLogger()
    temporal_engine = TemporalEngine(event_logger)
    memory_engine = MemoryEngine(event_logger, temporal_engine)
    ai_reflection = AIReflection(memory_engine)
    query_interface = QueryInterface(event_logger, memory_engine, ai_reflection)
    
    # Log some test events
    print("\n2. Logging test events...")
    activities = [
        ("coding", "Working on ECHO project", 120, ["work", "focus"]),
        ("task", "Write documentation", 60, ["writing"]),
        ("learning", "Study AI patterns", 90, ["education"]),
        ("meeting", "Team sync", 30, ["work", "communication"]),
        ("note", "Idea for new feature", 15, ["idea"]),
    ]
    
    for i in range(10):  # Log 10 events over past few days
        activity = random.choice(activities)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 5), 
                                               hours=random.randint(0, 23))
        event_logger.log_event(
            event_type=activity[0],
            content=activity[1],
            duration_minutes=activity[2],
            tags=activity[3],
            timestamp=timestamp
        )
    print("✓ Logged test events")
    
    # Update memories
    print("\n3. Analyzing patterns...")
    insights = memory_engine.update_memories()
    print(f"✓ Found {len(insights.get('new_insights', []))} insights")
    
    # Generate reflection
    print("\n4. Generating AI reflection...")
    reflection = ai_reflection.generate_reflection("general")
    print(f"\nECHO says: {reflection}")
    
    # Test queries
    print("\n5. Testing query interface...")
    test_queries = [
        "How productive was I this week?",
        "When do I focus best?",
        "What patterns do you see?"
    ]
    
    for query in test_queries:
        print(f"\nQ: {query}")
        response = query_interface.answer_query(query)
        print(f"A: {response}")
    
    print("\n" + "=" * 50)
    print("✅ ECHO is working! Check data/memory.db for stored events")
    print("Run 'streamlit run app.py' to launch the web interface")

if __name__ == "__main__":
    test_echo()