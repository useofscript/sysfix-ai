
import click
from sysfixai.core import diagnose, apply_fix, ai_auto_fix

@click.group()
def cli():
    """sysfix-ai: Safe Linux diagnostics with optional AI-assisted fixes."""
    pass

@cli.command()
def check():
    """Run system diagnostics."""
    use_ai = click.confirm("Do you want to use AI to automatically diagnose and fix issues?", default=False)
    issues = diagnose()
    click.echo("Diagnostics results:")
    for idx, issue in enumerate(issues, 1):
        click.echo(f"{idx}. {issue}")
    if use_ai:
        ai_auto_fix(issues)

@cli.command()
@click.argument('issue_number', type=int)
def fix(issue_number):
    """Apply fix for a given issue number."""
    use_ai = click.confirm("Do you want to use AI to automatically fix this issue?", default=False)
    issues = diagnose()
    if issue_number < 1 or issue_number > len(issues):
        click.echo("Invalid issue number.")
        return
    issue = issues[issue_number - 1]
    click.echo(f"Applying fix for: {issue}")
    if use_ai:
        ai_auto_fix([issue])
    else:
        apply_fix(issue)
    click.echo("Fix applied (simulated).")

if __name__ == "__main__":
    cli()
