"""Unit tests for the CLI module."""

import os
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from kase.cli import DEFAULT_CASE_DIR, main

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_help_command(self):
        """Test help command shows available commands."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "query" in result.stdout
        assert "init" in result.stdout
        assert "shell" in result.stdout

    def test_shell_command(self):
        """Test shell command outputs shell integration."""
        result = runner.invoke(main, ["shell"])
        assert result.exit_code == 0
        assert "jk()" in result.stdout
        assert "kase query" in result.stdout
        assert "cd" in result.stdout

    @patch("kase.cli.QueryApp")
    def test_query_command_default_case_dir(self, mock_query_app):
        """Test query command with default case directory."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = None
        mock_query_app.return_value = mock_app_instance

        result = runner.invoke(main, ["query"])

        assert result.exit_code == 0
        mock_query_app.assert_called_once()

    @patch("kase.cli.QueryApp")
    def test_query_command_custom_case_dir(self, mock_query_app):
        """Test query command with custom case directory."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = None
        mock_query_app.return_value = mock_app_instance

        result = runner.invoke(main, ["query", "--case-dir", "/custom/path"])

        assert result.exit_code == 0
        mock_query_app.assert_called_once_with(
            initial_prompt="", case_dir="/custom/path"
        )

    @patch("kase.cli.QueryApp")
    def test_query_command_with_result(self, mock_query_app):
        """Test query command prints result when returned."""
        mock_app_instance = MagicMock()
        mock_case = MagicMock()
        mock_case.path = "/path/to/case"
        mock_app_instance.run.return_value = mock_case
        mock_query_app.return_value = mock_app_instance

        result = runner.invoke(main, ["query"])

        assert result.exit_code == 0
        assert "/path/to/case" in result.stdout

    @patch("kase.cli.InitApp")
    @patch.dict(os.environ, {}, clear=True)
    def test_init_command(self, mock_init_app):
        """Test init command."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = None
        mock_init_app.return_value = mock_app_instance

        result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        mock_init_app.assert_called_once_with(DEFAULT_CASE_DIR)

    @patch("kase.cli.InitApp")
    def test_init_command_honors_env_case_dir(self, mock_init_app):
        """Test init command uses CASE_DIR environment variable when provided."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = None
        mock_init_app.return_value = mock_app_instance
        env_case_dir = "/custom/env/path"

        with patch.dict(os.environ, {"CASE_DIR": env_case_dir}, clear=True):
            result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        mock_init_app.assert_called_once_with(env_case_dir)

    @patch("kase.cli.InitApp")
    def test_init_command_with_result(self, mock_init_app):
        """Test init command prints result when returned."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = "Case created successfully."
        mock_init_app.return_value = mock_app_instance

        result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        assert "Case created successfully." in result.stdout

    @patch("kase.cli.QueryApp")
    def test_default_command_invokes_query(self, mock_query_app):
        """Test that default command (no subcommand) invokes query."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = None
        mock_query_app.return_value = mock_app_instance

        result = runner.invoke(main, [])

        assert result.exit_code == 0
        mock_query_app.assert_called_once()

    @patch("kase.cli.ImporterApp")
    def test_import_command_creates_new_case(self, mock_importer_app, tmp_path):
        """Test import command writes metadata when case is new."""
        csv_file = tmp_path / "cases.csv"
        csv_file.write_text("")
        case = MagicMock()
        case.sf = "12345"
        case.path = tmp_path / "12345"
        case.write_metadata = MagicMock()

        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = [case]
        mock_importer_app.return_value = mock_app_instance

        result = runner.invoke(main, ["import", str(csv_file)])

        assert result.exit_code == 0
        assert "Creating 12345" in result.stdout
        case.write_metadata.assert_called_once_with()

    @patch("kase.cli.ImporterApp")
    def test_import_command_skips_when_user_declines_overwrite(
        self, mock_importer_app, tmp_path
    ):
        """Test import command warns and skips when decline overwrite."""
        csv_file = tmp_path / "cases.csv"
        csv_file.write_text("")
        metadata_dir = tmp_path / "12345"
        metadata_dir.mkdir()
        (metadata_dir / "case.json").write_text("{}")
        case = MagicMock()
        case.sf = "12345"
        case.path = metadata_dir
        case.write_metadata = MagicMock()

        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = [case]
        mock_importer_app.return_value = mock_app_instance

        result = runner.invoke(main, ["import", str(csv_file)], input="n\n")

        assert result.exit_code == 0
        assert "already exists" in result.stdout
        assert "Skipping 12345" in result.stdout
        case.write_metadata.assert_not_called()

    @patch("kase.cli.ImporterApp")
    def test_import_command_overwrites_when_confirmed(
        self, mock_importer_app, tmp_path
    ):
        """Test import command overwrites metadata when confirmed."""
        csv_file = tmp_path / "cases.csv"
        csv_file.write_text("")
        metadata_dir = tmp_path / "12345"
        metadata_dir.mkdir()
        (metadata_dir / "case.json").write_text("{}")
        case = MagicMock()
        case.sf = "12345"
        case.path = metadata_dir
        case.write_metadata = MagicMock()

        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = [case]
        mock_importer_app.return_value = mock_app_instance

        result = runner.invoke(main, ["import", str(csv_file)], input="y\n")

        assert result.exit_code == 0
        assert "Overwriting 12345" in result.stdout
        case.write_metadata.assert_called_once_with(clobber=True)
