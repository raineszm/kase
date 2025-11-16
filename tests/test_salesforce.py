"""Tests for Salesforce scraper functionality."""

from kase.salesforce import SalesforceScraper


def test_is_salesforce_url_with_lightning():
    """Test Salesforce URL validation for Lightning URLs."""
    scraper = SalesforceScraper()
    assert scraper.is_salesforce_url(
        "https://acme.lightning.force.com/lightning/r/Case/5001234567890AB/view"
    )


def test_is_salesforce_url_with_my_salesforce():
    """Test Salesforce URL validation for my.salesforce.com URLs."""
    scraper = SalesforceScraper()
    assert scraper.is_salesforce_url("https://acme.my.salesforce.com/5001234567890AB")


def test_is_salesforce_url_invalid():
    """Test that non-Salesforce URLs are rejected."""
    scraper = SalesforceScraper()
    assert not scraper.is_salesforce_url("https://example.com/invalid")
