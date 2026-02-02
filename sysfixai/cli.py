import click
from sysfixai.core import diagnose, apply_fix

@click.group()
def cli():
    """sysfix-ai: Safe Linux diagnostics with optional AI-assisted fixes."""
    pass

@cli.command()
def check():
    """Run system diagnostics."""
    issues = diagnose()
    click.echo("Diagnostics results:")
    for idx, issue in enumerate(issues, 1):
        click.echo(f"{idx}. {issue}")

@cli.command()
@click.argument('issue_number', type=int)
def fix(issue_number):
    """Apply fix for a given issue number."""
    issues = diagnose()
    if issue_number < 1 or issue_number > len(issues):
        click.echo("Invalid issue number.")
        return
    issue = issues[issue_number - 1]
    click.echo(f"Applying fix for: {issue}")
    apply_fix(issue)
    click.echo("Fix applied (simulated).")

if __name__ == "__main__":
    cli()
