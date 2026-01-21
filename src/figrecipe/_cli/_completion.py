#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""completion command - Shell completion script generation and installation."""

import os
import subprocess
from pathlib import Path

import click

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

SHELLS = ["bash", "zsh", "fish"]

RC_FILES = {
    "bash": Path.home() / ".bashrc",
    "zsh": Path.home() / ".zshrc",
    "fish": Path.home() / ".config/fish/completions/figrecipe.fish",
}

COMPLETION_LINES = {
    "bash": 'eval "$(_FIGRECIPE_COMPLETE=bash_source figrecipe)"',
    "zsh": 'eval "$(_FIGRECIPE_COMPLETE=zsh_source figrecipe)"',
    "fish": "_FIGRECIPE_COMPLETE=fish_source figrecipe | source",
}


def _detect_shell() -> str:
    """Detect the current shell from $SHELL environment variable."""
    shell_path = os.environ.get("SHELL", "/bin/bash")
    shell_name = Path(shell_path).name
    if shell_name in SHELLS:
        return shell_name
    return "bash"


def _get_completion_script(shell: str) -> str:
    """Generate completion script for the given shell."""
    env_var = f"_FIGRECIPE_COMPLETE={shell}_source"
    env = os.environ.copy()
    env[env_var.split("=")[0]] = env_var.split("=")[1]

    result = subprocess.run(
        ["figrecipe"],
        env=env,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _is_installed(shell: str) -> bool:
    """Check if completion is installed for the given shell."""
    rc_file = RC_FILES[shell]
    if not rc_file.exists():
        return False

    completion_line = COMPLETION_LINES[shell]
    try:
        content = rc_file.read_text()
        return completion_line in content
    except (OSError, IOError):
        return False


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.pass_context
def completion(ctx) -> None:
    """Shell completion for figrecipe CLI.

    \b
    Commands:
      figrecipe completion install   # Install completion (default)
      figrecipe completion status    # Check installation status
      figrecipe completion bash      # Show bash completion script
      figrecipe completion zsh       # Show zsh completion script

    \b
    Quick install:
      figrecipe completion install
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@completion.command("install")
@click.option(
    "--shell",
    type=click.Choice(SHELLS),
    default=None,
    help="Target shell. Auto-detected if not specified.",
)
def install_completion(shell: str) -> None:
    """Install shell completion for figrecipe CLI.

    Auto-detects the current shell from $SHELL if not specified.
    Appends the completion script to the appropriate rc file.
    """
    if shell is None:
        shell = _detect_shell()
        click.echo(f"Detected shell: {shell}")

    rc_file = RC_FILES[shell]
    completion_line = COMPLETION_LINES[shell]

    # Check if already installed
    if _is_installed(shell):
        click.echo(f"✓ Completion already installed in {rc_file}")
        return

    # Fish needs special handling for directory creation
    if shell == "fish":
        rc_file.parent.mkdir(parents=True, exist_ok=True)
        rc_file.write_text(f"# figrecipe completion\n{completion_line}\n")
        click.echo(f"✓ Installed completion to {rc_file}")
    else:
        # Append to rc file
        try:
            with open(rc_file, "a") as f:
                f.write(f"\n# figrecipe completion\n{completion_line}\n")
            click.echo(f"✓ Installed completion to {rc_file}")
        except (OSError, IOError) as e:
            click.echo(f"✗ Failed to install: {e}", err=True)
            raise SystemExit(1)

    click.echo(f"\nReload your shell or run: source {rc_file}")


@completion.command("status")
@click.option(
    "--shell",
    type=click.Choice(SHELLS),
    default=None,
    help="Target shell. Checks all if not specified.",
)
def status_completion(shell: str) -> None:
    """Check shell completion installation status."""
    shells_to_check = [shell] if shell else SHELLS

    for sh in shells_to_check:
        rc_file = RC_FILES[sh]
        installed = _is_installed(sh)
        status = "✓ installed" if installed else "✗ not installed"
        click.echo(f"{sh:8} {status:16} ({rc_file})")


@completion.command("bash")
def bash_completion() -> None:
    """Show bash completion script."""
    click.echo(_get_completion_script("bash"))


@completion.command("zsh")
def zsh_completion() -> None:
    """Show zsh completion script."""
    click.echo(_get_completion_script("zsh"))


@completion.command("fish")
def fish_completion() -> None:
    """Show fish completion script."""
    click.echo(_get_completion_script("fish"))
