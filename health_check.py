# health_check.py
"""Quick health check for ECHO system"""

import os
import sys
from datetime import datetime, timedelta

def check_echo():
    print("🧠 ECHO Health Check")
    print("=" * 50)
    
    issues = []
    successes = []
    
    # 1. Check directories
    print("\n1. Checking directories...")
    for dir_name in ["data", "modules"]:
        if os.path.exists(dir_name):
            successes.append(f"✓ {dir_name}/ exists")
        else:
            issues.append(f"✗ {dir_name}/ missing")
    
    # 2. Check modules
    print("\n2. Checking modules...")
    modules = ["event_logger", "temporal_engine", "memory_engine", "ai_reflection", "query_interface"]
    for module in modules:
        if os.path.exists(f"modules/{module}.py"):
            successes.append(f"✓ {module}.py exists")
        else:
            issues.append(f"✗ modules/{module}.py missing")
    
    # 3. Try importing
    print("\n3. Testing imports...")
    try:
        from modules import EventLogger, TemporalEngine, MemoryEngine, AIReflection, QueryInterface
        successes.append("✓ All modules import successfully")
    except Exception as e:
        issues.append(f"✗ Import failed: {e}")
    
    # 4. Test database
    print("\n4. Testing database...")
    try:
        from modules import EventLogger
        logger = EventLogger()
        
        # Log a test event
        test_id = logger.log_event("health_check", "System health check", 1, ["test"])
        successes.append(f"✓ Database write successful (ID: {test_id})")
        
        # Read it back
        df = logger.get_events(limit=1)
        if not df.empty:
            successes.append("✓ Database read successful")
        
        # Clean up test event
        import sqlite3
        with sqlite3.connect("data/memory.db") as conn:
            conn.execute("DELETE FROM events WHERE event_type='health_check'")
        successes.append("✓ Database cleanup successful")
        
    except Exception as e:
        issues.append(f"✗ Database error: {e}")
    
    # 5. Test pattern detection
    print("\n5. Testing pattern detection...")
    try:
        from modules import TemporalEngine
        engine = TemporalEngine(logger)
        patterns = engine.analyze_hourly_patterns()
        successes.append("✓ Pattern detection works")
    except Exception as e:
        issues.append(f"✗ Pattern detection error: {e}")
    
    # 6. Check profile
    print("\n6. Checking user profile...")
    if os.path.exists("data/user_profile.json"):
        import json
        try:
            with open("data/user_profile.json", 'r') as f:
                profile = json.load(f)
            successes.append("✓ Profile exists and is valid JSON")
            print(f"   - Created: {profile.get('created_at', 'unknown')}")
            print(f"   - Insights: {len(profile.get('insights_generated', []))}")
        except Exception as e:
            issues.append(f"✗ Profile error: {e}")
    else:
        issues.append("✗ Profile file missing")
    
    # 7. Summary
    print("\n" + "=" * 50)
    print(f"✅ Successes: {len(successes)}")
    print(f"⚠️ Issues: {len(issues)}")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("\n🎉 ECHO is fully operational!")
        print("\nYou can now run:")
        print("  python test_echo.py")
        print("  python -m streamlit run app.py")
    
    return len(issues) == 0

if __name__ == "__main__":
    sys.exit(0 if check_echo() else 1)