"""Integration tests for the InitApp TUI."""

import json
from pathlib import Path

from kase.tui.init import InitApp


class TestInitApp:
    """Integration tests for InitApp."""

    def test_init_app_compose(self, snap_compare, temp_case_dir):
        """Test that InitApp composes correctly using snapshot testing."""
        app = InitApp(temp_case_dir)
        # Use Textual's snap_compare for snapshot testing
        assert snap_compare(app)

    async def test_init_app_create_case_success(self, temp_case_dir):
        """Test creating a case through the UI."""
        app = InitApp(temp_case_dir)
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
            case_dir = Path(temp_case_dir) / "1234"
            assert case_dir.exists()

            metadata_file = case_dir / "case.json"
            assert metadata_file.exists()

            with metadata_file.open("r") as f:
                data = json.load(f)

            assert data["title"] == "Test Case"
            assert data["desc"] == "This is a test description"
            assert data["sf"] == "1234"

    async def test_init_app_invalid_case_name(self, temp_case_dir):
        """Test that invalid case name doesn't create a case."""
        app = InitApp(temp_case_dir)
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
            assert len(list(Path(temp_case_dir).iterdir())) == 0

    async def test_init_app_without_lp_bug(self, temp_case_dir):
        """Test creating a case without LP bug."""
        app = InitApp(temp_case_dir)
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
            case_dir = Path(temp_case_dir) / "5678"
            assert case_dir.exists()

            metadata_file = case_dir / "case.json"
            with metadata_file.open("r") as f:
                data = json.load(f)

            assert data["title"] == "Another Test Case"
            assert data["sf"] == "5678"

    async def test_init_app_existing_directory_no_metadata(self, temp_case_dir):
        """Test creating case in existing directory without case.json."""
        # Create existing directory
        existing_dir = Path(temp_case_dir) / "1234"
        existing_dir.mkdir()

        app = InitApp(temp_case_dir)
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

            # Verify metadata was created
            metadata_file = existing_dir / "case.json"
            assert metadata_file.exists()

            with metadata_file.open("r") as f:
                data = json.load(f)

            assert data["title"] == "Test Case"
            assert data["sf"] == "1234"

    async def test_init_app_existing_case_json(self, temp_case_dir):
        """Test that creating a case with existing case.json fails gracefully."""
        # Create existing directory with case.json
        existing_dir = Path(temp_case_dir) / "1234"
        existing_dir.mkdir()
        existing_metadata = existing_dir / "case.json"
        existing_metadata.write_text(
            json.dumps(
                {
                    "title": "Original Case",
                    "desc": "Original description",
                    "sf": "1234",
                    "lp": "",
                }
            )
        )

        app = InitApp(temp_case_dir)
        async with app.run_test() as pilot:
            # Fill in the form
            case_name_input = app.query_one("#case_name_input")
            case_name_input.value = "[1234] New Test Case"

            text_area = app.query_one("TextArea")
            await pilot.pause()
            text_area.text = "New Description"

            # Click the button
            await pilot.click("Button")
            await pilot.pause()

            # Verify metadata was NOT overwritten
            with existing_metadata.open("r") as f:
                data = json.load(f)

            assert data["title"] == "Original Case"
            assert data["desc"] == "Original description"
