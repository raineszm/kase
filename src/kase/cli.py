import textwrap
from os import environ
from pathlib import Path

import typer

from .cases import CaseRepo
from .salesforce import import_salesforce_case
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
def import_case(
    url: str = typer.Argument(..., help="Salesforce case URL to import"),
    case_dir: str | None = typer.Option(
        None,
        help="Directory to store case files. "
        "Defaults to $CASE_DIR environment variable or ~/cases",
    ),
    show_browser: bool = typer.Option(
        False, "--show-browser", help="Show browser window during import"
    ),
):
    """
    Import a case from a Salesforce URL.

    Opens a browser to fetch case information from Salesforce.
    If not logged in, provides a workflow to authenticate.
    """
    if case_dir is None:
        case_dir = environ.get("CASE_DIR", "~/cases")

    print(f"Importing case from: {url}")

    # Import case from Salesforce
    sf_case = import_salesforce_case(url, headless=not show_browser)

    if sf_case is None:
        print("Failed to import case from Salesforce.")
        raise typer.Exit(code=1)

    print("\nCase imported successfully:")
    print(f"  SF ID: {sf_case.sf_id}")
    print(f"  Title: {sf_case.title}")
    desc_preview = (
        f"  Description: {sf_case.description[:100]}..."
        if len(sf_case.description) > 100
        else f"  Description: {sf_case.description}"
    )
    print(desc_preview)

    # Create case using existing CaseRepo
    repo = CaseRepo(case_dir)
    case_name = f"[{sf_case.sf_id}] {sf_case.title}"

    if repo.create_case(name=case_name, lp="", description=sf_case.description):
        case_path = Path(repo.case_dir) / sf_case.sf_id
        print(f"\nCase created at: {case_path}")
    else:
        print("\nFailed to create case. Case may already exist.")
        raise typer.Exit(code=1)


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
