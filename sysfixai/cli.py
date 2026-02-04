
import click
from sysfixai.core import diagnose, apply_fix, ai_auto_fix, ai_deep_dive

@click.group()
def cli():
    """sysfix-ai: Safe Linux diagnostics with optional AI-assisted fixes."""
    pass

@cli.command()
def check():
    """Run system diagnostics."""
    use_ai = click.confirm("Do you want to use AI to automatically diagnose and fix issues?", default=False)
    if use_ai:
        ai_mode = click.prompt("Select AI mode", type=click.Choice(['1', '2'], case_sensitive=False),
                              default='1', show_choices=True)
        if ai_mode == '1':
            click.echo("Running Fast Sweep mode...")
            issues = diagnose()
            click.echo("Diagnostics results:")
            for idx, issue in enumerate(issues, 1):
                click.echo(f"{idx}. {issue}")
            ai_auto_fix(issues)
        elif ai_mode == '2':
            click.echo("Running Deep Dive mode...")
            ai_deep_dive()
    else:
        issues = diagnose()
        click.echo("Diagnostics results:")
        for idx, issue in enumerate(issues, 1):
            click.echo(f"{idx}. {issue}")

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
