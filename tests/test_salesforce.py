"""Tests for Salesforce scraper functionality."""

from kase.salesforce import SalesforceScraper


def test_extract_case_id_from_standard_url():
    """Test extracting case ID from standard Salesforce URL."""
    scraper = SalesforceScraper()
    url = "https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view"
    case_id = scraper.extract_case_id_from_url(url)
    assert case_id == "5001234567890AB"


def test_extract_case_id_from_classic_url():
    """Test extracting case ID from Salesforce Classic URL."""
    scraper = SalesforceScraper()
    url = "https://acme.my.salesforce.com/5001234567890AB"
    case_id = scraper.extract_case_id_from_url(url)
    assert case_id == "5001234567890AB"


def test_extract_case_id_from_url_with_query_params():
    """Test extracting case ID from URL with query parameters."""
    scraper = SalesforceScraper()
    url = "https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view?param=value"
    case_id = scraper.extract_case_id_from_url(url)
    assert case_id == "5001234567890AB"


def test_extract_case_id_returns_none_for_invalid_url():
    """Test that extract_case_id_from_url returns None for invalid URLs."""
    scraper = SalesforceScraper()
    url = "https://example.com/invalid"
    case_id = scraper.extract_case_id_from_url(url)
    assert case_id is None


def test_is_salesforce_url():
    """Test Salesforce URL validation."""
    scraper = SalesforceScraper()
    assert scraper.is_salesforce_url(
        "https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view"
    )
    assert scraper.is_salesforce_url("https://acme.my.salesforce.com/5001234567890AB")
    assert not scraper.is_salesforce_url("https://example.com/invalid")
