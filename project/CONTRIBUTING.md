# Contributing to Smart Task Timer

Thank you for your interest in contributing! This document provides guidelines to help you get started.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic familiarity with command-line tools

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd tst_vscode_agents/project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Testing tools

# Run tests to verify setup
pytest
```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes
- Write clean, readable code
- Follow existing code style
- Add/update tests for your changes
- Update documentation if needed

### 3. Test Your Changes
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_timer.py
```

### 4. Commit Your Work
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add weekly report export to CSV"
```

### 5. Submit Pull Request
- Push your branch to GitHub
- Create a pull request with clear description
- Reference any related issues

## Code Style Guidelines

### Python Conventions
- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Maximum line length: **88 characters** (Black default)
- Use **docstrings** for all public functions and classes

### Example:
```python
def calculate_duration(start: datetime, end: datetime) -> timedelta:
    """
    Calculate the duration between two timestamps.
    
    Args:
        start: The start timestamp
        end: The end timestamp
    
    Returns:
        A timedelta representing the duration
    
    Raises:
        ValueError: If end is before start
    """
    if end < start:
        raise ValueError("End time must be after start time")
    return end - start
```

### Formatting Tools
```bash
# Auto-format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check style
flake8 src/ tests/
```

## Testing Guidelines

### Writing Tests
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_timer_calculates_correct_duration`
- Follow AAA pattern: **Arrange**, **Act**, **Assert**

### Example Test:
```python
def test_timer_calculates_correct_duration():
    # Arrange
    timer = Timer()
    start_time = datetime(2025, 11, 22, 10, 0, 0)
    end_time = datetime(2025, 11, 22, 10, 30, 0)
    
    # Act
    duration = timer.calculate_duration(start_time, end_time)
    
    # Assert
    assert duration == timedelta(minutes=30)
```

### Coverage Requirements
- Aim for **80%+ test coverage** on new code
- Test both happy paths and edge cases
- Include tests for error conditions

## Commit Message Format

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding/updating tests
- `refactor`: Code refactoring
- `style`: Formatting changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(reports): add CSV export functionality

Implements CSV export for session data with configurable fields.
Includes tests for various date ranges and edge cases.

Closes #42
```

```
fix(timer): prevent negative duration calculation

Added validation to ensure end time is after start time.
Raises ValueError with descriptive message.
```

## Documentation

### Code Documentation
- Add docstrings to all public functions/classes
- Include parameter types, return types, and examples
- Document exceptions that may be raised

### README Updates
Update `README.md` when adding:
- New commands or features
- Configuration options
- Breaking changes

## Pull Request Process

1. **Ensure all tests pass**: `pytest`
2. **Update documentation**: README, docstrings, ARCHITECTURE.md if needed
3. **Add changelog entry**: Update CHANGELOG.md with your changes
4. **Request review**: Assign reviewers or wait for automatic assignment
5. **Address feedback**: Make requested changes promptly
6. **Squash commits**: If requested, consolidate commits before merge

## Code Review Guidelines

### As a Reviewer
- Be respectful and constructive
- Focus on code quality, not style preferences
- Ask questions rather than making demands
- Approve when changes meet project standards

### As a Contributor
- Respond to feedback professionally
- Ask for clarification if needed
- Don't take criticism personally
- Update PR based on feedback

## Project Structure Rules

### Where to Add Code

| Change Type | Location | Example |
|------------|----------|---------|
| New CLI command | `src/cli.py` | Add `@click.command()` function |
| Timer logic | `src/timer.py` | Update `Timer` or `Session` class |
| Storage format | `src/storage.py` | Modify `save_session()` or schema |
| Report type | `src/reports.py` | Add new report function |
| AI insight | `src/ai.py` | Add analysis function |
| Tests | `tests/test_*.py` | Match source file name |

### What to Avoid
- ❌ Adding external dependencies without discussion
- ❌ Changing storage format without migration path
- ❌ Breaking existing CLI commands
- ❌ Committing sensitive data or credentials
- ❌ Large files or binaries

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with reproduction steps
- **Features**: Propose in an issue before implementing
- **Security**: Email maintainers privately

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Thank you for contributing to Smart Task Timer!** 🎉
