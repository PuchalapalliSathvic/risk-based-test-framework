"""Browser driver setup/teardown wrapper around Playwright."""
from contextlib import contextmanager

try:
    from playwright.sync_api import sync_playwright
    _HAS_PLAYWRIGHT = True
except ImportError:  # keeps the repo importable without the browser installed
    _HAS_PLAYWRIGHT = False


@contextmanager
def browser_page(headless=True, base_url=None):
    """Yield a Playwright page, tearing everything down on exit."""
    if not _HAS_PLAYWRIGHT:
        raise RuntimeError(
            "Playwright not installed. Run: pip install playwright && playwright install chromium"
        )
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(base_url=base_url)
        page = context.new_page()
        try:
            yield page
        finally:
            context.close()
            browser.close()
