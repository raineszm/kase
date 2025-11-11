# Tests

This directory contains the test suite for the kase project.

## Structure

- `unit/` - Unit tests for core functionality
  - `test_cases.py` - Tests for the Case model and CaseRepo class
  - `test_cli.py` - Tests for CLI commands
- `integration/` - Integration tests for the TUI
  - `test_init_app.py` - Tests for the InitApp TUI
  - `test_query_app.py` - Tests for the QueryApp TUI

## Running Tests

Run all tests:
```bash
uv run pytest
```

Run with verbose output:
```bash
uv run pytest -v
```

Run with coverage:
```bash
uv run pytest --cov=kase --cov-report=term-missing
```

Run specific test file:
```bash
uv run pytest tests/unit/test_cases.py
```

Run specific test:
```bash
uv run pytest tests/unit/test_cases.py::TestCase::test_case_creation
```

## Test Coverage

The test suite aims for high code coverage (currently 98%). Coverage reports show which lines of code are exercised by the tests.

## Writing Tests

### Unit Tests

Unit tests should:
- Test individual functions and methods in isolation
- Use mocking for external dependencies
- Be fast and independent

### Integration Tests

Integration tests for Textual TUI apps should:
- Use the `app.run_test()` context manager
- Test user interactions and widget states
- Verify the UI behaves correctly end-to-end

Example:
```python
async def test_example():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Test interactions here
        assert app.query_one("#widget_id")
```
