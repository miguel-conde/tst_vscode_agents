# Smart Task Timer - Architecture

## System Overview

Smart Task Timer is a command-line productivity tool built with a **modular, layered architecture** that separates concerns between user interface, business logic, and data persistence. The design emphasizes simplicity, testability, and extensibility.

```
┌─────────────────────────────────────────────────┐
│              CLI Interface (cli.py)              │
│  Commands: start, stop, report, export, insights │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          Business Logic Layer                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────┐│
│  │  timer.py   │  │  reports.py  │  │ ai.py   ││
│  │ (Core logic)│  │ (Analytics)  │  │(Insights)││
│  └─────────────┘  └──────────────┘  └─────────┘│
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│        Data Layer (storage.py)                   │
│     JSON file-based persistence                  │
└─────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI Interface (`cli.py`)

**Responsibility**: User interaction and command routing

**Key Functions**:
- `start_timer(task, category)`: Initiates a new timing session
- `stop_timer()`: Ends current session and saves data
- `show_report(period, by_category)`: Displays time analytics
- `export_data(format)`: Exports session data
- `show_insights()`: Displays AI-generated productivity tips

**Technology**: Click framework for elegant command-line parsing

**Example**:
```python
@click.command()
@click.option('--task', required=True, help='Task description')
@click.option('--category', type=click.Choice(['feature', 'bug', 'refactor', 'docs', 'meeting']))
def start(task, category):
    """Start timing a new task"""
    timer = Timer()
    timer.start(task, category)
```

### 2. Timer Core (`timer.py`)

**Responsibility**: Time tracking business logic

**Key Classes**:
- `Timer`: Manages individual timing sessions
- `Session`: Data model for a completed task session

**Key Methods**:
```python
class Timer:
    def start(task: str, category: str) -> None
    def stop() -> Session
    def is_running() -> bool
    def current_duration() -> timedelta
    
class Session:
    task: str
    category: str
    start_time: datetime
    end_time: datetime
    duration: timedelta
```

**State Management**: 
- Active timer state stored in `.timer_state.json`
- Single active session enforcement
- Automatic validation of category values

### 3. Data Storage (`storage.py`)

**Responsibility**: Persistence and retrieval of session data

**Storage Format**: JSON file (`~/.task_timer/sessions.json`)

**Key Functions**:
```python
def save_session(session: Session) -> None
def load_sessions(start_date=None, end_date=None) -> List[Session]
def get_active_timer() -> Optional[Timer]
def clear_active_timer() -> None
```

**Data Schema**:
```json
{
  "sessions": [
    {
      "id": "uuid-here",
      "task": "Fix login bug",
      "category": "bug",
      "start_time": "2025-11-22T10:30:00",
      "end_time": "2025-11-22T11:15:00",
      "duration_seconds": 2700
    }
  ]
}
```

**Design Decisions**:
- JSON for human readability and easy debugging
- File-based for zero-dependency deployment
- UUID for session identification
- ISO 8601 timestamps for portability

### 4. Reports & Analytics (`reports.py`)

**Responsibility**: Data aggregation and visualization

**Key Functions**:
```python
def daily_summary(date: date) -> Report
def weekly_breakdown(week_start: date) -> Report
def category_distribution(sessions: List[Session]) -> Dict[str, timedelta]
def generate_ascii_chart(data: Dict) -> str
```

**Report Types**:
- **Daily Summary**: Total time + category breakdown
- **Weekly Overview**: Daily totals with trend indicators
- **Category Analysis**: Time distribution across task types
- **Export Formats**: JSON, Markdown, CSV

**Sample Output**:
```
Today: 4h 30m across 5 tasks

By Category:
  feature  ████████████████  60% (2h 42m)
  bug      ████████          27% (1h 13m)
  refactor ███               13% (35m)
```

### 5. AI Insights (`ai.py`)

**Responsibility**: Pattern analysis and productivity suggestions

**Key Functions**:
```python
def analyze_patterns(sessions: List[Session]) -> Insights
def suggest_improvements(patterns: Dict) -> List[str]
def detect_focus_time() -> str
def calculate_efficiency_score() -> float
```

**Insight Examples**:
- "You're most productive between 9-11 AM (avg 2.5h focus time)"
- "Consider batching bug fixes - you switch contexts 8 times/day"
- "Refactoring ratio is low (5%) - technical debt may accumulate"

**Algorithm**:
1. Aggregate sessions by time-of-day, category, duration
2. Identify patterns (focus periods, context switches, category balance)
3. Apply heuristics for recommendations
4. Generate natural language suggestions

## Data Flow

### Starting a Task
```
User Input → CLI validates → Timer.start() 
           → Storage saves state → Confirmation
```

### Stopping a Task
```
User Input → CLI validates → Timer.stop() 
           → Session created → Storage persists 
           → Clear active state → Show duration
```

### Generating Reports
```
User Input → CLI parses options → Storage loads sessions
           → Reports aggregates → Format output 
           → Display to console
```

## File Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Click commands (150 lines)
│   ├── timer.py            # Timer & Session classes (120 lines)
│   ├── storage.py          # JSON persistence (100 lines)
│   ├── reports.py          # Analytics & formatting (180 lines)
│   └── ai.py               # Insights generation (90 lines)
├── tests/
│   ├── __init__.py
│   ├── test_timer.py       # Timer logic tests
│   ├── test_storage.py     # Persistence tests
│   ├── test_reports.py     # Report generation tests
│   └── test_ai.py          # Insights tests
├── data/
│   └── .gitkeep            # Placeholder for user data directory
├── PRODUCT.md              # Product specification
├── ARCHITECTURE.md         # This document
├── README.md               # User documentation
└── requirements.txt        # Python dependencies
```

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| CLI Framework | Click 8.x | Elegant API, automatic help generation |
| Testing | pytest 7.x | Industry standard, excellent fixtures |
| Date/Time | Python datetime | Built-in, no external dependencies |
| Storage | JSON + pathlib | Simple, portable, debuggable |
| Type Hints | Python 3.8+ typing | Better IDE support, self-documenting |
| Formatting | Black + isort | Consistent code style |

## Design Principles

### 1. Separation of Concerns
Each module has a single, well-defined responsibility. The CLI doesn't know about JSON storage; storage doesn't generate reports.

### 2. Testability
Pure functions and dependency injection enable easy unit testing without mocks.

### 3. Progressive Enhancement
Core functionality (start/stop/basic reports) works immediately. Advanced features (AI insights, exports) are optional additions.

### 4. Zero External Services
No database, no cloud APIs, no authentication. Everything runs locally with minimal setup.

### 5. Human-Readable Data
JSON storage means users can inspect, edit, or migrate their data easily.

## Extension Points

### Adding New Categories
Update `VALID_CATEGORIES` constant in `timer.py`:
```python
VALID_CATEGORIES = ['feature', 'bug', 'refactor', 'docs', 'meeting', 'learning']
```

### Adding Export Formats
Implement new formatter in `reports.py`:
```python
def export_csv(sessions: List[Session]) -> str:
    # Generate CSV format
    pass
```

### Custom Insights
Add analysis function to `ai.py`:
```python
def detect_burnout_risk(sessions: List[Session]) -> Optional[str]:
    # Analyze work patterns
    pass
```

## Security & Privacy

- **Local-only**: All data stored on user's machine
- **No tracking**: No analytics, telemetry, or external requests
- **Plain text**: Sessions stored in readable JSON (not encrypted)
- **User control**: Data directory is standard location, easy to backup/delete

## Performance Characteristics

- **Session storage**: O(1) append, O(n) read
- **Report generation**: O(n) where n = number of sessions
- **Memory footprint**: Minimal (~10MB with 10k sessions)
- **Startup time**: <100ms for CLI initialization

---

**Architecture Version**: 1.0  
**Last Updated**: November 22, 2025  
**Status**: Ready for implementation
