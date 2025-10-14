from .tui import KaseApp
import typer
import textwrap

main = typer.Typer()


@main.command()
def query():
    """
    Pop up a fuzzy finder to select a case to cd into.

    For the cd functionality to work, the shell integration
    must have been set up.
    """
    app = KaseApp("~/cases")
    result = app.run()
    if result is not None:
        print(result)


@main.command()
def init():
    """
    Create a new case.json file in the appropriate directory.

    Creates the directory if it does not exist.
    """
    pass


@main.command()
def shell():
    """
    Print the shell integration code to stdout.

    This code can be sourced in your shell configuration file
    to enable the cd functionality.
    """
    print(
        textwrap.dedent(
            """
        jk() {
            dir=$(\\kase query) && cd "$dir"
        }
        """
        )
    )


@main.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        query()
