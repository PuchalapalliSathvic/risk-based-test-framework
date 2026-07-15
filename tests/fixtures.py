"""Reusable fixtures wiring the Playwright page into page objects."""
import pytest
from framework.driver import browser_page
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.checkout_page import CheckoutPage

STANDARD_USER = "standard_user"
PASSWORD = "secret_sauce"


@pytest.fixture
def page():
    with browser_page(headless=True) as p:
        yield p


@pytest.fixture
def login_page(page):
    return LoginPage(page)


@pytest.fixture
def logged_in(page):
    """A page already authenticated as the standard user."""
    LoginPage(page).open().login(STANDARD_USER, PASSWORD)
    return page
