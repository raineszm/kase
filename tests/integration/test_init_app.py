"""Integration tests for the InitApp TUI."""

import json
import tempfile
from pathlib import Path

from kase.tui.init import InitApp


class TestInitApp:
    """Integration tests for InitApp."""

    async def test_init_app_compose(self):
        """Test that InitApp composes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = InitApp(tmpdir)
            async with app.run_test():
                # Check that all widgets are present
                assert app.query_one("#case_name_input")
                assert app.query_one("#lp_bug_input")
                assert app.query("TextArea")
                assert app.query("Button")

    async def test_init_app_create_case_success(self):
        """Test creating a case through the UI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = InitApp(tmpdir)
            async with app.run_test() as pilot:
                # Fill in the form
                case_name_input = app.query_one("#case_name_input")
                lp_bug_input = app.query_one("#lp_bug_input")
                text_area = app.query_one("TextArea")

                case_name_input.value = "[1234] Test Case"
                lp_bug_input.value = "LP#5678"

                # Set text in TextArea
                await pilot.pause()
                text_area.text = "This is a test description"

                # Click the button
                await pilot.click("Button")
                await pilot.pause()

                # Verify case was created
                case_dir = Path(tmpdir) / "1234"
                assert case_dir.exists()

                metadata_file = case_dir / "case.json"
                assert metadata_file.exists()

                with metadata_file.open("r") as f:
                    data = json.load(f)

                assert data["title"] == "Test Case"
                assert data["desc"] == "This is a test description"
                assert data["sf"] == "1234"

    async def test_init_app_invalid_case_name(self):
        """Test that invalid case name doesn't create a case."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = InitApp(tmpdir)
            async with app.run_test() as pilot:
                # Fill in the form with invalid name
                case_name_input = app.query_one("#case_name_input")
                lp_bug_input = app.query_one("#lp_bug_input")
                text_area = app.query_one("TextArea")

                case_name_input.value = "Invalid Name"
                lp_bug_input.value = ""
                await pilot.pause()
                text_area.text = "Description"

                # Click the button
                await pilot.click("Button")
                await pilot.pause()

                # Verify no case was created
                assert len(list(Path(tmpdir).iterdir())) == 0

    async def test_init_app_without_lp_bug(self):
        """Test creating a case without LP bug."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = InitApp(tmpdir)
            async with app.run_test() as pilot:
                # Fill in the form without LP bug
                case_name_input = app.query_one("#case_name_input")
                text_area = app.query_one("TextArea")

                case_name_input.value = "[5678] Another Test Case"
                await pilot.pause()
                text_area.text = "Another description"

                # Click the button
                await pilot.click("Button")
                await pilot.pause()

                # Verify case was created
                case_dir = Path(tmpdir) / "5678"
                assert case_dir.exists()

                metadata_file = case_dir / "case.json"
                with metadata_file.open("r") as f:
                    data = json.load(f)

                assert data["title"] == "Another Test Case"
                assert data["sf"] == "5678"

    async def test_init_app_existing_case(self):
        """Test that creating a case with existing directory fails gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing directory
            existing_dir = Path(tmpdir) / "1234"
            existing_dir.mkdir()

            app = InitApp(tmpdir)
            async with app.run_test() as pilot:
                # Fill in the form
                case_name_input = app.query_one("#case_name_input")
                case_name_input.value = "[1234] Test Case"

                text_area = app.query_one("TextArea")
                await pilot.pause()
                text_area.text = "Description"

                # Click the button
                await pilot.click("Button")
                await pilot.pause()

                # Verify no metadata was created
                metadata_file = existing_dir / "case.json"
                assert not metadata_file.exists()
