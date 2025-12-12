# Smart Task Timer

A minimalist productivity tool for developers to track time spent on coding tasks.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Start timing a task
timer start --task "Fix login bug" --category bug

# Check status
timer status

# Stop the timer
timer stop

# List all sessions
timer list

# List sessions with filters
timer list --today                    # Today's sessions
timer list --week                     # This week's sessions
timer list --category feature         # Filter by category
timer list --limit 10                 # Show only 10 most recent
timer list --today --category bug     # Combine filters
```

## Categories

Available task categories:
- `feature`: New functionality
- `bug`: Bug fixes
- `refactor`: Code improvements
- `docs`: Documentation work
- `meeting`: Team discussions

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=src
```
