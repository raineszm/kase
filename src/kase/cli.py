import textwrap
from os import environ

import typer

from .tui.init import InitApp
from .tui.query import QueryApp

main = typer.Typer()


@main.command()
def query(
    case_dir: str | None = typer.Argument(
        None,
        help="Directory containing case files."
        "Defaults to $CASE_DIR environment variable or ~/cases",
    ),
):
    """
    Pop up a fuzzy finder to select a case to cd into.

    For the cd functionality to work, the shell integration
    must have been set up.
    """

    if case_dir is None:
        case_dir = environ.get("CASE_DIR", "~/cases")

    app = QueryApp(case_dir)
    result = app.run()
    if result is not None:
        print(result)


@main.command()
def init():
    """
    Create a new case.json file in the appropriate directory.

    Creates the directory if it does not exist.
    """
    app = InitApp("~/cases")
    if result := app.run():
        print(result)


@main.command()
def shell(
    jump_cmd: str = typer.Argument(
        "jk",
        help="Name of the shell function to create.",
    ),
):
    """
    Print the shell integration code to stdout.

    This code can be sourced in your shell configuration file
    to enable the cd functionality. It will create a shell
    function named JUMP_CMD that will jump to the selected
    case directory.
    """
    print(
        textwrap.dedent(
            f"""
        {jump_cmd}() {{
            dir=$(\\kase query) && cd "$dir"
        }}
        """
        )
    )


@main.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        query()
