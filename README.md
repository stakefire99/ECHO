# 🧠 ECHO - Personal AI Memory System

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28.0-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> ECHO learns your behavioral patterns over time and provides meaningful AI-powered insights about your productivity, focus, and consistency.

## ✨ Features

- **📝 Event Logging** - Track activities with timestamps, tags, and durations
- **⏰ Pattern Detection** - Find peak hours, weekly trends, and activity bursts  
- **🧠 Memory Engine** - Builds an evolving user profile based on your behavior
- **💭 AI Reflections** - Get personalized insights about your patterns
- **💬 Chat Interface** - Ask questions naturally about your productivity
- **📊 Interactive Dashboard** - Visualize your activity timeline

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/stakefire99/echo.git
cd echo
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Or run tests first
python test_echo.py
💡 Usage Examples
Log an activity:

python
logger.log_event("coding", "Built AI memory system", 120, ["focus", "work"])
Ask ECHO questions:

"How productive was I this week?"

"When do I focus best?"

"What patterns do you see?"

Sample response:

"Your most active hours are 10:00 and 14:00. Your activity has been trending upward, and you're remarkably consistent in your daily patterns."

🏗️ Architecture
Module	Purpose
event_logger.py	SQLite storage with time-series queries
temporal_engine.py	Pattern detection & trend analysis
memory_engine.py	User profiling & insight generation
ai_reflection.py	Natural language reflections
query_interface.py	Intent recognition & responses
🛠️ Tech Stack
Python 3.8+ - Core language

SQLite - Time-series storage

Pandas/NumPy - Data analysis

Streamlit - Web interface

OpenAI - Advanced reflections (optional)

📁 Project Structure
text
echo/
├── app.py                 # Streamlit UI
├── test_echo.py          # Test suite
├── health_check.py       # Diagnostics
├── modules/              # Core modules
│   ├── event_logger.py
│   ├── temporal_engine.py
│   ├── memory_engine.py
│   ├── ai_reflection.py
│   └── query_interface.py
└── data/                 # Auto-created
    ├── memory.db
    └── user_profile.json
🔧 Configuration
Optional OpenAI Integration:

bash
export OPENAI_API_KEY='your-key-here'
Without an API key, ECHO uses template-based reflections.

🧪 Testing
bash
python test_echo.py      # Full test suite
python health_check.py   # System diagnostics
📈 Sample Insights
Peak Hours: 10:00 AM - 1:00 PM

Best Day: Tuesdays (35% more productive)

Consistency Score: 85% (very consistent)

Activity Trend: +12% week over week

🤝 Contributing
Open issues, submit PRs, or suggest features! See CONTRIBUTING.md for guidelines.

📚 Documentation
Each module has detailed docstrings. Run pydoc modules.module_name for API reference.

🐛 Troubleshooting
Issue	Fix
ImportError: openai	pip install openai or ignore (template mode works)
JSONDecodeError: Delete data/user_profile.json and restart
Streamlit not found. Use python -m streamlit run app.py

🗺️ Coming Soon
Natural language logging
Weekly email summaries
Export insights as PDF
Goal tracking & streaks
📄 License
MIT License - feel free to use, modify, and share!
