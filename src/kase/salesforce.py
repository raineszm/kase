"""Salesforce case import functionality using Playwright."""

import re

from playwright.sync_api import Page, sync_playwright
from pydantic import BaseModel


class SalesforceCase(BaseModel):
    """Model for Salesforce case data."""

    sf_id: str
    title: str
    description: str


class SalesforceScraper:
    """Scraper for extracting case information from Salesforce."""

    # Pattern to extract SF case ID from URL
    CASE_ID_PATTERN = re.compile(r"/([0-9a-zA-Z]{15,18})(?:/|$)")

    def __init__(self, headless: bool = True):
        """Initialize the scraper.

        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

    def __enter__(self):
        """Context manager entry."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def extract_case_id(self, url: str) -> str | None:
        """Extract Salesforce case ID from URL.

        Args:
            url: Salesforce case URL

        Returns:
            Case ID or None if not found
        """
        match = self.CASE_ID_PATTERN.search(url)
        return match.group(1) if match else None

    def wait_for_login(self, page: Page, timeout: int = 300000) -> bool:
        """Wait for user to complete login process.

        Args:
            page: Playwright page object
            timeout: Maximum time to wait in milliseconds (default: 5 minutes)

        Returns:
            True if login successful, False otherwise
        """
        try:
            # Wait for either the case page to load or timeout
            # Salesforce typically redirects to the case after login
            page.wait_for_url(
                re.compile(r"(lightning\.force\.com|my\.salesforce\.com)"),
                timeout=timeout,
            )
            # Give the page a moment to fully load
            page.wait_for_load_state("networkidle", timeout=30000)
            return True
        except Exception as e:
            print(f"Login timeout or error: {e}")
            return False

    def scrape_case(self, url: str) -> SalesforceCase | None:
        """Scrape case information from Salesforce URL.

        Args:
            url: Salesforce case URL

        Returns:
            SalesforceCase object or None if scraping failed
        """
        if not self.context:
            raise RuntimeError("Scraper not initialized. Use context manager.")

        page = self.context.new_page()

        try:
            # Navigate to the URL
            print(f"Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Check if we need to login
            current_url = page.url
            needs_login = (
                "login" in current_url.lower()
                or "authentication" in current_url.lower()
            )
            if needs_login:
                print(
                    "\nLogin required. "
                    "Please complete the login process in the browser."
                )
                print("Waiting for login to complete...")

                if not self.headless:
                    print("Browser window should be visible for login.")

                if not self.wait_for_login(page):
                    print("Login failed or timed out.")
                    return None

                # After login, navigate back to the case URL if needed
                if url not in page.url:
                    print(f"Navigating back to case: {url}")
                    page.goto(url, wait_until="networkidle", timeout=60000)
                else:
                    page.wait_for_load_state("networkidle", timeout=30000)

            # Extract case ID from URL
            case_id = self.extract_case_id(url)
            if not case_id:
                print("Could not extract case ID from URL")
                return None

            print(f"Extracted case ID: {case_id}")

            # Wait for the page to be ready
            page.wait_for_load_state("domcontentloaded", timeout=30000)

            # Try to extract case information
            # Salesforce Lightning uses specific selectors
            title = self._extract_title(page)
            description = self._extract_description(page)

            if not title:
                print("Could not extract case title")
                return None

            return SalesforceCase(
                sf_id=case_id, title=title, description=description or ""
            )

        except Exception as e:
            print(f"Error scraping case: {e}")
            return None
        finally:
            page.close()

    def _extract_title(self, page: Page) -> str | None:
        """Extract case title from page.

        Args:
            page: Playwright page object

        Returns:
            Case title or None
        """
        # Try multiple selectors for Salesforce Lightning and Classic
        selectors = [
            # Lightning - Subject field
            'lightning-formatted-text[data-output-element-id*="Subject"]',
            'span[title*="Subject"]',
            # Classic UI
            "#cas3_ileinner",
            # Generic fallback - look for subject label
            'label:has-text("Subject") + *',
            'div:has-text("Subject:") + *',
        ]

        for selector in selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text().strip()
                    if text:
                        return text
            except Exception:
                continue

        # Last resort: try to find it in page content
        try:
            content = page.content()
            # Look for common patterns
            import re

            match = re.search(r'Subject["\s:]+([^"<>\n]+)', content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        except Exception:
            pass

        return None

    def _extract_description(self, page: Page) -> str | None:
        """Extract case description from page.

        Args:
            page: Playwright page object

        Returns:
            Case description or None
        """
        # Try multiple selectors for description
        selectors = [
            # Lightning - Description field
            'lightning-formatted-text[data-output-element-id*="Description"]',
            'div[title*="Description"]',
            # Classic UI
            "#cas14_ileinner",
            # Generic fallback
            'label:has-text("Description") + *',
            'div:has-text("Description:") + *',
        ]

        for selector in selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text().strip()
                    if text:
                        return text
            except Exception:
                continue

        return None


def import_salesforce_case(url: str, headless: bool = False) -> SalesforceCase | None:
    """Import a case from Salesforce URL.

    Args:
        url: Salesforce case URL
        headless: Whether to run browser in headless mode

    Returns:
        SalesforceCase object or None if import failed
    """
    with SalesforceScraper(headless=headless) as scraper:
        return scraper.scrape_case(url)
