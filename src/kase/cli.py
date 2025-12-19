import importlib.metadata
import textwrap
from typing import Annotated

import typer

from .tui.init import InitApp
from .tui.query import QueryApp

DEFAULT_CASE_DIR = "~/cases"


main = typer.Typer()


@main.command()
def query(
    initial_prompt: Annotated[
        str,
        typer.Argument(
            help="Initial prompt for the fuzzy finder.",
        ),
    ] = "",
    case_dir: Annotated[
        str,
        typer.Option(
            help="Directory containing case files."
            "Defaults to $CASE_DIR environment variable or ~/cases",
            envvar="CASE_DIR",
        ),
    ] = DEFAULT_CASE_DIR,
):
    """
    Pop up a fuzzy finder to select a case to cd into.

    For the cd functionality to work, the shell integration
    must have been set up.
    """

    app = QueryApp(initial_prompt=initial_prompt, case_dir=case_dir)
    result = app.run()
    if result is not None:
        print(result)


@main.command()
def init(
    case_dir: Annotated[
        str,
        typer.Option(
            help="Directory containing case files."
            "Defaults to $CASE_DIR environment variable or ~/cases",
            envvar="CASE_DIR",
        ),
    ] = DEFAULT_CASE_DIR,
):
    """
    Create a new case.json file in the appropriate directory.

    Creates the directory if it does not exist.
    """
    app = InitApp(case_dir)
    if result := app.run():
        print(result)


@main.command()
def shell(
    jump_cmd: Annotated[
        str,
        typer.Argument(
            help="Name of the shell function to create.",
        ),
    ] = "jk",
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


def version_callback(print_version: bool):
    if print_version:
        print(f"kase {importlib.metadata.version('kase')}")
        raise typer.Exit()


@main.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            help="Print the version and exit.", callback=version_callback, is_eager=True
        ),
    ] = False,
):
    if ctx.invoked_subcommand is None:
        query()
