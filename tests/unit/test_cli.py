"""Unit tests for the CLI module."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from kase.cli import main

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
        # Check that it was called with default or env variable
        call_args = mock_query_app.call_args[0]
        assert len(call_args) > 0

    @patch("kase.cli.QueryApp")
    def test_query_command_custom_case_dir(self, mock_query_app):
        """Test query command with custom case directory."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = None
        mock_query_app.return_value = mock_app_instance

        result = runner.invoke(main, ["query", "/custom/path"])

        assert result.exit_code == 0
        mock_query_app.assert_called_once_with("/custom/path")

    @patch("kase.cli.QueryApp")
    def test_query_command_with_result(self, mock_query_app):
        """Test query command prints result when returned."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = "/path/to/case"
        mock_query_app.return_value = mock_app_instance

        result = runner.invoke(main, ["query"])

        assert result.exit_code == 0
        assert "/path/to/case" in result.stdout

    @patch("kase.cli.InitApp")
    def test_init_command(self, mock_init_app):
        """Test init command."""
        mock_app_instance = MagicMock()
        mock_app_instance.run.return_value = None
        mock_init_app.return_value = mock_app_instance

        result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        mock_init_app.assert_called_once_with("~/cases")

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
