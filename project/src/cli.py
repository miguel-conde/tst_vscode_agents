"""Command-line interface for Smart Task Timer."""

import click
from datetime import datetime, timedelta
from src.timer import Timer, get_valid_categories
from src.storage import (
    get_active_timer,
    save_active_timer,
    clear_active_timer,
    save_session,
    load_sessions,
    load_sessions_by_category,
    get_storage_dir
)
from src.reports import (
    generate_daily_report,
    generate_weekly_report,
    ReportExporter
)


def format_duration(duration):
    """
    Format a timedelta duration into a human-readable string.
    
    Args:
        duration: timedelta object
        
    Returns:
        Formatted string like "2h 15m 30s"
    """
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


@click.group()
def cli():
    """Smart Task Timer - Track your coding time with ease."""
    pass


@cli.command()
@click.option('--task', required=True, help='Description of the task')
@click.option(
    '--category',
    required=True,
    help='Task category'
)
def start(task, category):
    """
    Start timing a new task.
    
    Example:
        timer start --task "Fix login bug" --category bug
    """
    try:
        # Validate category
        valid_categories = get_valid_categories()
        if category not in valid_categories:
            click.echo(
                click.style(f"Error: Invalid category '{category}'", fg='red')
            )
            click.echo(f"Valid categories: {', '.join(valid_categories)}")
            raise click.Abort()
        
        # Check if timer is already running
        existing_timer = get_active_timer()
        if existing_timer:
            click.echo(
                click.style(
                    f"Error: Timer is already running for '{existing_timer.task}'",
                    fg='red'
                )
            )
            click.echo("Stop the current timer before starting a new one.")
            raise click.Abort()
        
        # Create and start new timer
        timer = Timer()
        timer.start(task=task, category=category)
        
        # Save timer state
        save_active_timer(timer)
        
        # Success message
        click.echo(
            click.style("✓ Started timer", fg='green', bold=True) +
            f" for task: {click.style(task, fg='cyan')}"
        )
        click.echo(f"Category: {click.style(category, fg='yellow')}")
        click.echo(f"Started at: {timer.start_time.strftime('%H:%M:%S')}")
        
    except ValueError as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
        raise click.Abort()
    except RuntimeError as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
        raise click.Abort()


@cli.command()
def stop():
    """
    Stop the currently running timer and save the session.
    
    Example:
        timer stop
    """
    try:
        # Load active timer
        timer = get_active_timer()
        if not timer:
            click.echo(click.style("Error: No timer is currently running", fg='red'))
            raise click.Abort()
        
        # Stop timer and create session
        session = timer.stop()
        
        # Save session
        save_session(session)
        
        # Clear active timer state
        clear_active_timer()
        
        # Success message
        click.echo(
            click.style("✓ Stopped timer", fg='green', bold=True) +
            f" for task: {click.style(session.task, fg='cyan')}"
        )
        click.echo(f"Category: {click.style(session.category, fg='yellow')}")
        click.echo(f"Duration: {click.style(format_duration(session.duration), fg='green', bold=True)}")
        click.echo(f"Session saved successfully")
        
    except RuntimeError as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
        raise click.Abort()


@cli.command()
def status():
    """
    Show the status of the current timer.
    
    Example:
        timer status
    """
    timer = get_active_timer()
    
    if not timer:
        click.echo(click.style("No timer is currently running", fg='yellow'))
        click.echo("\nStart a new timer with:")
        click.echo("  timer start --task \"Your task\" --category <category>")
        return
    
    # Calculate elapsed time
    duration = timer.current_duration()
    
    # Display status
    click.echo(click.style("Timer is running", fg='green', bold=True))
    click.echo(f"\nTask: {click.style(timer.task, fg='cyan')}")
    click.echo(f"Category: {click.style(timer.category, fg='yellow')}")
    click.echo(f"Started at: {timer.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"Elapsed time: {click.style(format_duration(duration), fg='green', bold=True)}")


@cli.command(name='list')
@click.option('--category', help='Filter by category')
@click.option('--today', is_flag=True, help='Show only today\'s sessions')
@click.option('--week', is_flag=True, help='Show only this week\'s sessions')
@click.option('--limit', type=int, help='Limit number of sessions displayed')
def list_sessions(category, today, week, limit):
    """
    List all recorded sessions with optional filtering.
    
    Examples:
        timer list
        timer list --category feature
        timer list --today
        timer list --week --category bug
        timer list --limit 10
    """
    # Determine date filters
    start_date = None
    end_date = None
    
    if today:
        now = datetime.now()
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif week:
        now = datetime.now()
        # Start of current week (Monday)
        days_since_monday = now.weekday()
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        end_date = start_date + timedelta(days=7)
    
    # Load sessions with filters
    if category:
        sessions = load_sessions_by_category(
            category,
            start_date=start_date,
            end_date=end_date
        )
    else:
        sessions = load_sessions(start_date=start_date, end_date=end_date)
    
    # Check if no sessions
    if not sessions:
        click.echo(click.style("No sessions found", fg='yellow'))
        return
    
    # Apply limit if specified
    total_sessions = len(sessions)
    if limit and limit < len(sessions):
        sessions = sessions[-limit:]  # Show most recent
    
    # Display header
    click.echo(click.style("\n=== Sessions ===", fg='cyan', bold=True))
    
    # Display sessions
    total_duration = timedelta(0)
    for i, session in enumerate(sessions, 1):
        total_duration += session.duration
        
        # Format session display
        time_str = session.start_time.strftime('%Y-%m-%d %H:%M')
        duration_str = format_duration(session.duration)
        
        click.echo(f"\n{i}. {click.style(session.task, fg='white', bold=True)}")
        click.echo(f"   Category: {click.style(session.category, fg='yellow')}")
        click.echo(f"   Started: {time_str}")
        click.echo(f"   Duration: {click.style(duration_str, fg='green')}")
    
    # Display summary
    click.echo(click.style("\n=== Summary ===", fg='cyan', bold=True))
    
    if limit and limit < total_sessions:
        click.echo(f"Showing {len(sessions)} of {total_sessions} sessions (most recent)")
    else:
        click.echo(f"Total sessions: {len(sessions)}")
    
    click.echo(f"Total time: {click.style(format_duration(total_duration), fg='green', bold=True)}")


@cli.command()
@click.option('--date', default=None, help='Date for report (YYYY-MM-DD), defaults to today')
@click.option('--format', 'output_format', type=click.Choice(['text', 'json', 'markdown', 'csv']), 
              default='text', help='Output format')
@click.option('--output', '-o', type=click.Path(), default=None, 
              help='Save report to file instead of stdout')
def daily(date, output_format, output):
    """Generate daily report."""
    # Use today if no date specified
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        click.echo(click.style("Error: Invalid date format. Use YYYY-MM-DD", fg='red'), err=True)
        return
    
    # Generate report
    report = generate_daily_report(date)
    exporter = ReportExporter(report)
    
    # Format output
    if output_format == 'json':
        content = exporter.to_json()
    elif output_format == 'markdown':
        content = exporter.to_markdown()
    elif output_format == 'csv':
        content = exporter.to_csv()
    else:  # text
        content = exporter.to_markdown()  # Use markdown for text display
    
    # Output
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(click.style(f"Report saved to {output}", fg='green'))
    else:
        click.echo(content)


@cli.command()
@click.option('--start', default=None, help='Start date (YYYY-MM-DD), defaults to week start')
@click.option('--end', default=None, help='End date (YYYY-MM-DD), defaults to week end')
@click.option('--format', 'output_format', type=click.Choice(['text', 'json', 'markdown', 'csv']), 
              default='text', help='Output format')
@click.option('--output', '-o', type=click.Path(), default=None, 
              help='Save report to file instead of stdout')
def weekly(start, end, output_format, output):
    """Generate weekly report."""
    now = datetime.now()
    
    # Calculate current week if not specified
    if not start:
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        start = week_start.strftime('%Y-%m-%d')
    
    if not end:
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        end = week_end.strftime('%Y-%m-%d')
    
    # Validate dates
    try:
        datetime.strptime(start, '%Y-%m-%d')
        datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        click.echo(click.style("Error: Invalid date format. Use YYYY-MM-DD", fg='red'), err=True)
        return
    
    # Generate report
    report = generate_weekly_report(start, end)
    exporter = ReportExporter(report)
    
    # Format output
    if output_format == 'json':
        content = exporter.to_json()
    elif output_format == 'markdown':
        content = exporter.to_markdown()
    elif output_format == 'csv':
        content = exporter.to_csv()
    else:  # text
        content = exporter.to_markdown()
    
    # Output
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(click.style(f"Report saved to {output}", fg='green'))
    else:
        click.echo(content)


if __name__ == '__main__':
    cli()
