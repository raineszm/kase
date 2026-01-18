"""Unit tests for the cases module."""

import json
from pathlib import Path

from kase.cases import Case, CaseRepo


class TestCase:
    """Tests for the Case model."""

    def test_case_creation(self):
        """Test creating a Case instance."""
        path = Path("/tmp/test")
        case = Case(
            path=path,
            title="Test Case",
            desc="Test description",
            sf="1234",
            lp="LP#5678",
        )

        assert case.path == path
        assert case.title == "Test Case"
        assert case.desc == "Test description"
        assert case.sf == "1234"
        assert case.lp == "LP#5678"

    def test_case_creation_without_lp(self):
        """Test creating a Case instance without LP bug."""
        path = Path("/tmp/test")
        case = Case(
            path=path,
            title="Test Case",
            desc="Test description",
            sf="1234",
        )

        assert case.path == path
        assert case.title == "Test Case"
        assert case.desc == "Test description"
        assert case.sf == "1234"
        assert case.lp == ""

    def test_write_metadata(self, fs):
        """Test writing metadata to a JSON file."""
        path = Path("/cases/1234")
        fs.create_dir(path)
        case = Case(
            path=path,
            title="Test Case",
            desc="Test description",
            sf="1234",
            lp="LP#5678",
        )

        case.write_metadata()

        metadata_file = path / "case.json"
        assert metadata_file.exists()

        with metadata_file.open("r") as f:
            data = json.load(f)

        assert data["title"] == "Test Case"
        assert data["desc"] == "Test description"
        assert data["sf"] == "1234"
        assert data["lp"] == "LP#5678"
        assert "path" not in data


class TestCaseRepo:
    """Tests for the CaseRepo class."""

    def test_case_repo_initialization(self):
        """Test initializing a CaseRepo."""
        repo = CaseRepo("~/test_cases")
        assert repo.case_dir.endswith("test_cases")

    def test_case_repo_expands_tilde(self):
        """Test that CaseRepo expands ~ in paths."""
        repo = CaseRepo("~/test_cases")
        assert not repo.case_dir.startswith("~")

    def test_metadata_property_empty_dir(self, fs):
        """Test metadata property with empty directory."""
        fs.create_dir("/cases")
        repo = CaseRepo("/cases")
        assert list(repo.metadata) == []

    def test_metadata_property_with_cases(self, fs):
        """Test metadata property with existing cases."""
        fs.create_dir("/cases")

        # Create test case directories
        case1_dir = Path("/cases/1234")
        fs.create_dir(case1_dir)
        fs.create_file(
            case1_dir / "case.json",
            contents=json.dumps(
                {
                    "title": "Test Case 1",
                    "desc": "Description 1",
                    "sf": "1234",
                    "lp": "",
                }
            ),
        )

        case2_dir = Path("/cases/5678")
        fs.create_dir(case2_dir)
        fs.create_file(
            case2_dir / "case.json",
            contents=json.dumps(
                {
                    "title": "Test Case 2",
                    "desc": "Description 2",
                    "sf": "5678",
                    "lp": "LP#9999",
                }
            ),
        )

        repo = CaseRepo("/cases")
        metadata = list(repo.metadata)

        assert len(metadata) == 2
        assert all(m.name == "case.json" for m in metadata)

    def test_cases_property(self, fs):
        """Test cases property returns Case objects."""
        fs.create_dir("/cases")

        # Create test case directory
        case_dir = Path("/cases/1234")
        fs.create_dir(case_dir)
        fs.create_file(
            case_dir / "case.json",
            contents=json.dumps(
                {
                    "title": "Test Case",
                    "desc": "Test description",
                    "sf": "1234",
                    "lp": "LP#5678",
                }
            ),
        )

        repo = CaseRepo("/cases")
        cases = list(repo.cases)

        assert len(cases) == 1
        case = cases[0]
        assert isinstance(case, Case)
        assert case.title == "Test Case"
        assert case.desc == "Test description"
        assert case.sf == "1234"
        assert case.lp == "LP#5678"
        assert case.path == case_dir

    def test_load_meta(self, fs):
        """Test _load_meta static method."""
        case_dir = Path("/cases/1234")
        fs.create_dir(case_dir)
        case_meta = case_dir / "case.json"
        fs.create_file(
            case_meta,
            contents=json.dumps(
                {
                    "title": "Test Case",
                    "desc": "Test description",
                    "sf": "1234",
                    "lp": "",
                }
            ),
        )

        case = CaseRepo._load_meta(case_meta)

        assert isinstance(case, Case)
        assert case.title == "Test Case"
        assert case.desc == "Test description"
        assert case.sf == "1234"
        assert case.lp == ""
        assert case.path == case_dir

    def test_case_preview(self, fs):
        """Test Case.preview property."""
        case_dir = Path("/cases/1234")
        fs.create_dir(case_dir)
        fs.create_file(
            case_dir / "case.json",
            contents=json.dumps(
                {
                    "title": "Test Case",
                    "desc": "Test description",
                    "sf": "1234",
                    "lp": "",
                }
            ),
        )

        repo = CaseRepo("/cases")
        case = next(repo.cases)
        preview = case.preview

        assert "[1234]" in preview
        assert "Test Case" in preview
        assert "Test description" in preview

    def test_create_case_success(self, fs):
        """Test creating a new case successfully."""
        fs.create_dir("/cases")

        repo = CaseRepo("/cases")
        result = repo.create_case(
            name="[1234] Test Case",
            lp="LP#5678",
            description="Test description",
        )

        assert result is True

        case_dir = Path("/cases/1234")
        assert case_dir.exists()

        metadata_file = case_dir / "case.json"
        assert metadata_file.exists()

        with metadata_file.open("r") as f:
            data = json.load(f)

        assert data["title"] == "Test Case"
        assert data["desc"] == "Test description"
        assert data["sf"] == "1234"

    def test_create_case_invalid_name_format(self, fs):
        """Test creating a case with invalid name format."""
        fs.create_dir("/cases")

        repo = CaseRepo("/cases")
        result = repo.create_case(
            name="Invalid Name Format",
            lp="",
            description="Test description",
        )

        assert result is False

    def test_create_case_existing_directory_no_metadata(self, fs):
        """Test creating a case when directory exists but no case.json."""
        fs.create_dir("/cases")

        # Create the directory first
        case_dir = Path("/cases/1234")
        fs.create_dir(case_dir)

        repo = CaseRepo("/cases")
        result = repo.create_case(
            name="[1234] Test Case",
            lp="",
            description="Test description",
        )

        # Should succeed
        assert result is True

        # Verify metadata was created
        metadata_file = case_dir / "case.json"
        assert metadata_file.exists()

    def test_create_case_existing_metadata(self, fs):
        """Test creating a case when case.json already exists."""
        fs.create_dir("/cases")

        # Create the directory and metadata file
        case_dir = Path("/cases/1234")
        fs.create_dir(case_dir)
        metadata_file = case_dir / "case.json"
        fs.create_file(
            metadata_file,
            contents=json.dumps(
                {
                    "title": "Original Case",
                    "desc": "Original description",
                    "sf": "1234",
                    "lp": "",
                }
            ),
        )

        repo = CaseRepo("/cases")
        result = repo.create_case(
            name="[1234] New Test Case",
            lp="",
            description="New description",
        )

        # Should fail - don't overwrite
        assert result is False

        # Verify original metadata is unchanged
        with metadata_file.open("r") as f:
            data = json.load(f)
        assert data["title"] == "Original Case"

    def test_title_regex_pattern_valid(self):
        """Test TITLE_RE regex with valid patterns."""
        match = CaseRepo.TITLE_RE.match("[1234] Test Case Title")
        assert match is not None
        assert match.group("sf") == "1234"
        assert match.group("title") == "Test Case Title"

    def test_title_regex_pattern_invalid(self):
        """Test TITLE_RE regex with invalid patterns."""
        # Missing brackets
        assert CaseRepo.TITLE_RE.match("1234 Test Case") is None

        # Missing SF number
        assert CaseRepo.TITLE_RE.match("[] Test Case") is None

        # Wrong format
        assert CaseRepo.TITLE_RE.match("Test Case [1234]") is None
