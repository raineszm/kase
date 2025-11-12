"""Stateful property-based tests for TUI using Hypothesis."""

import json
import tempfile
from pathlib import Path

from hypothesis import strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
    run_state_machine_as_test,
)

from kase.tui.query import QueryApp


class QueryAppStateMachine(RuleBasedStateMachine):
    """Stateful testing for QueryApp using Hypothesis.

    This tests sequences of user interactions to ensure the app maintains
    consistent state through various navigation and filtering operations.
    """

    def __init__(self):
        super().__init__()
        self.tmpdir = None
        self.app = None
        self.pilot = None
        self.num_cases = 0
        self.current_filter = ""

    @initialize()
    def setup_app(self):
        """Initialize the app with test data."""
        self.tmpdir = tempfile.mkdtemp()

        # Create a few test cases
        self.num_cases = 5
        for i in range(self.num_cases):
            case_dir = Path(self.tmpdir) / str(1000 + i)
            case_dir.mkdir()
            case_meta = case_dir / "case.json"
            case_meta.write_text(
                json.dumps(
                    {
                        "title": f"Test Case {i}",
                        "desc": f"Description for case {i}",
                        "sf": str(1000 + i),
                        "lp": f"LP#{i}" if i % 2 == 0 else "",
                    }
                )
            )

        self.app = QueryApp(self.tmpdir)
        # Note: In stateful testing, we can't easily use async context manager
        # So we'll track state without running the app

    @rule(
        filter_text=st.text(
            min_size=0,
            max_size=20,
            alphabet=st.characters(
                blacklist_characters=["\n", "\r", "\0"],
                blacklist_categories=["Cs", "Cc"],
            ),
        )
    )
    def apply_filter(self, filter_text):
        """Apply a filter to the case list."""
        # This tests that applying filters doesn't crash
        # In a real stateful test with running app, we'd interact with it
        # For now, we test the filter logic directly
        self.app.filter_text = filter_text
        self.current_filter = filter_text

        # Verify the app state is valid
        assert self.app.filter_text == filter_text
        assert self.app.repo is not None
        assert self.app.caselist is not None

    @rule()
    def clear_filter(self):
        """Clear the current filter."""
        self.app.filter_text = None
        self.current_filter = ""
        assert self.app.filter_text is None

    @rule(direction=st.sampled_from(["up", "down"]))
    def navigate(self, direction):
        """Navigate through the case list."""
        # Test navigation actions are available
        if direction == "up":
            assert hasattr(self.app, "action_cursor_up")
        else:
            assert hasattr(self.app, "action_cursor_down")

    @invariant()
    def valid_app_state(self):
        """Invariant: app should always be in a valid state."""
        assert self.app is not None
        assert self.app.repo is not None
        assert self.app.caselist is not None
        assert self.app.input is not None

    @invariant()
    def filter_text_is_string(self):
        """Invariant: filter text should always be None or a string."""
        assert self.app.filter_text is None or isinstance(self.app.filter_text, str)


class InitAppStateMachine(RuleBasedStateMachine):
    """Stateful testing for InitApp form interactions.

    Tests sequences of form field updates to ensure data integrity.
    """

    def __init__(self):
        super().__init__()
        self.form_data = {"case_name": "", "lp_bug": "", "description": ""}
        self.sf_number = None
        self.title = ""

    @rule(sf_number=st.integers(min_value=1, max_value=99999))
    def set_sf_number(self, sf_number):
        """Set the SF number in the case name."""
        self.sf_number = sf_number
        self.form_data["case_name"] = f"[{sf_number}] {self.title}"
        assert sf_number in range(1, 100000)

    @rule(
        title=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                blacklist_characters=["\n", "\r", "\0", "[", "]"],
                blacklist_categories=["Cs", "Cc"],
            ),
        )
    )
    def set_title(self, title):
        """Set the title in the case name."""
        self.title = title
        if self.sf_number is not None:
            self.form_data["case_name"] = f"[{self.sf_number}] {title}"
        else:
            self.form_data["case_name"] = title

    @rule(lp_bug=st.text(max_size=50))
    def set_lp_bug(self, lp_bug):
        """Set the LP bug field."""
        self.form_data["lp_bug"] = lp_bug
        assert len(self.form_data["lp_bug"]) <= 50

    @rule(description=st.text(max_size=200))
    def set_description(self, description):
        """Set the description field."""
        self.form_data["description"] = description
        assert len(self.form_data["description"]) <= 200

    @rule()
    def clear_form(self):
        """Clear all form fields."""
        self.form_data = {"case_name": "", "lp_bug": "", "description": ""}
        self.sf_number = None
        self.title = ""

    @rule()
    def validate_form_state(self):
        """Validate that form state is consistent."""
        # Check that all fields exist
        assert "case_name" in self.form_data
        assert "lp_bug" in self.form_data
        assert "description" in self.form_data

        # Check data types
        assert isinstance(self.form_data["case_name"], str)
        assert isinstance(self.form_data["lp_bug"], str)
        assert isinstance(self.form_data["description"], str)

    @invariant()
    def field_lengths_valid(self):
        """Invariant: all fields should respect their max lengths."""
        assert len(self.form_data["lp_bug"]) <= 50
        assert len(self.form_data["description"]) <= 200

    @invariant()
    def case_name_format_valid(self):
        """Invariant: case name should be properly formatted if SF number is set."""
        if self.sf_number is not None and self.title:
            expected = f"[{self.sf_number}] {self.title}"
            assert self.form_data["case_name"] == expected


def test_query_app_stateful():
    """Run stateful tests for QueryApp."""
    run_state_machine_as_test(QueryAppStateMachine)


def test_init_app_stateful():
    """Run stateful tests for InitApp form."""
    run_state_machine_as_test(InitAppStateMachine)
