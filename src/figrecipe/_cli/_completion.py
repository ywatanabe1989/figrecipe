#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""completion command - Shell completion script generation."""

import click

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

SHELLS = ["bash", "zsh", "fish"]

INSTALL_INSTRUCTIONS = {
    "bash": """# Add to ~/.bashrc:
eval "$(_FIGRECIPE_COMPLETE=bash_source figrecipe)"
""",
    "zsh": """# Add to ~/.zshrc:
eval "$(_FIGRECIPE_COMPLETE=zsh_source figrecipe)"
""",
    "fish": """# Add to ~/.config/fish/completions/figrecipe.fish:
_FIGRECIPE_COMPLETE=fish_source figrecipe | source
""",
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("shell", type=click.Choice(SHELLS))
@click.option(
    "--install",
    is_flag=True,
    help="Show installation instructions instead of the script.",
)
def completion(shell: str, install: bool) -> None:
    """Generate shell completion script.

    SHELL is the target shell (bash, zsh, or fish).

    \b
    Examples:
      figrecipe completion bash              # Output bash completion script
      figrecipe completion zsh --install     # Show zsh install instructions
      eval "$(figrecipe completion bash)"    # Enable completion directly
    """
    import os
    import subprocess

    if install:
        click.echo(INSTALL_INSTRUCTIONS[shell])
        return

    env_var = f"_FIGRECIPE_COMPLETE={shell}_source"
    env = os.environ.copy()
    env[env_var.split("=")[0]] = env_var.split("=")[1]

    result = subprocess.run(
        ["figrecipe"],
        env=env,
        capture_output=True,
        text=True,
    )
    click.echo(result.stdout)
