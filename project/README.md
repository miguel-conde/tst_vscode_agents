# Smart Task Timer

An intelligent productivity tool for developers that tracks time, analyzes patterns, and provides AI-powered insights to optimize your workflow.

## Features

✨ **Core Timer Functionality**
- Start/stop/status commands for tracking work sessions
- Persistent storage with JSON backend
- Multi-category task organization

📊 **Reports & Analytics**
- Daily and weekly reports with visualizations
- Multi-format export (JSON, Markdown, CSV)
- ASCII charts for category breakdown
- Flexible date filtering

🤖 **AI-Powered Insights**
- Pattern analysis and productivity scoring
- Work block detection
- Peak hours identification
- Personalized suggestions based on your work habits

## Quick Start

### Installation

```bash
# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Basic Usage

```bash
# Start timing a task
timer start --task "Implement user authentication" --category development

# Check current status
timer status

# Stop the timer
timer stop

# View recent sessions
timer list --limit 5
```

## Commands Reference

### Timer Commands

**Start a task**
```bash
timer start --task "Task description" --category <category>
```

**Check current timer status**
```bash
timer status
```

**Stop current timer**
```bash
timer stop
```

### List & Filter Sessions

**List all sessions**
```bash
timer list
```

**Filter by time period**
```bash
timer list --today          # Today's sessions
timer list --week           # This week's sessions
```

**Filter by category**
```bash
timer list --category development
```

**Limit results**
```bash
timer list --limit 10       # Show 10 most recent
```

**Combine filters**
```bash
timer list --today --category meetings --limit 5
```

### Reports

**Generate daily report**
```bash
# Today's report
timer daily

# Specific date
timer daily --date 2024-01-15

# Export to file
timer daily --format markdown --output report.md
```

**Generate weekly report**
```bash
# Current week
timer weekly

# Specific date range
timer weekly --start 2024-01-15 --end 2024-01-21

# Export formats: text, json, markdown, csv
timer weekly --format json --output weekly-report.json
```

### AI Insights

**Get productivity insights**
```bash
# Analyze last 7 days (default)
timer insights

# Custom time range
timer insights --days 30
```

The insights command provides:
- Productivity score (0-100) with rating
- Category distribution with visual charts
- Peak productivity hours
- Work block analysis
- Personalized suggestions for improvement

## Categories

Available task categories:
- `development`: Coding and implementation
- `bug`: Bug fixes and debugging
- `refactor`: Code refactoring and optimization
- `documentation`: Documentation work
- `meetings`: Team meetings and discussions
- `testing`: Writing and running tests
- `review`: Code reviews
- `learning`: Learning new technologies
- `planning`: Project planning
- `deployment`: Deployment and DevOps

## Examples

### Complete Workflow

```bash
# Morning: Start working on a feature
$ timer start --task "Add OAuth integration" --category development

# Check progress
$ timer status
# Timer running: Add OAuth integration
# Category: development
# Started: 2024-01-15 09:00:00
# Duration: 1h 30m

# Stop for lunch
$ timer stop
# Session saved: Add OAuth integration
# Duration: 1h 30m

# Afternoon: Quick meeting
$ timer start --task "Sprint planning" --category meetings
$ timer stop

# End of day: Review your work
$ timer daily
# Daily Report - 2024-01-15
# Total Duration: 3h 30m
# Sessions: 2
# 
# Category Breakdown:
# development: ████████████████ 1h 30m (43%)
# meetings:    ████████████████████ 2h (57%)

# Get weekly insights
$ timer insights --days 7
# AI PRODUCTIVITY INSIGHTS
# Productivity Score: 78/100 (Good)
# Most Common: development
# Peak Hour: 09:00
# Suggestions:
#   1. Great consistency! You're maintaining a steady work rhythm.
#   2. Consider taking breaks during long coding sessions...
```

### Export Reports

```bash
# Export daily report to Markdown
timer daily --format markdown --output daily-$(date +%F).md

# Export weekly data to CSV for analysis
timer weekly --format csv --output weekly-data.csv

# Generate JSON for integration with other tools
timer daily --format json --output data.json
```

## Data Storage

Session data is stored in `~/.smart-task-timer/`:
- `sessions.json`: All completed sessions
- `state.json`: Current active timer state

## Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd smart-task-timer

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_timer.py

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

**Current test coverage: 96%** (153 tests passing)

### Code Quality

```bash
# Format code with black
black src/ tests/

# Type checking with mypy
mypy src/

# Lint with flake8
flake8 src/ tests/
```

## Architecture

```
src/
├── __init__.py       # Package initialization
├── timer.py          # Core timer logic and Session class
├── storage.py        # JSON persistence layer
├── cli.py            # Click-based CLI interface
├── reports.py        # Report generation and export
└── ai.py             # AI pattern analysis and insights

tests/
├── test_timer.py     # Timer and Session tests
├── test_storage.py   # Storage layer tests
├── test_cli.py       # CLI command tests
├── test_reports.py   # Report generation tests
└── test_ai.py        # AI insights tests
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with Test-Driven Development (TDD) principles, demonstrating GitHub Copilot capabilities in:
- Boilerplate generation
- Test-first development
- Code refactoring
- Documentation generation
- Complex algorithms and pattern analysis
