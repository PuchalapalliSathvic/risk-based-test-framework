"""Sample automated tests. Each is tagged with a risk area via @risk(...).
The dynamic selector in conftest.py decides which of these actually run
based on the active risk threshold."""
import pytest
from framework.markers import risk
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.checkout_page import CheckoutPage
from tests.fixtures import page, login_page, logged_in, STANDARD_USER, PASSWORD


@risk("authentication")          # score 20
def test_valid_login(login_page):
    login_page.open().login(STANDARD_USER, PASSWORD)
    assert login_page.is_logged_in()


@risk("authentication")          # score 20
def test_locked_out_user_blocked(login_page):
    login_page.open().login("locked_out_user", PASSWORD)
    assert login_page.error_message() is not None
    assert not login_page.is_logged_in()


@risk("checkout_payment")        # score 20
def test_full_checkout(logged_in):
    InventoryPage(logged_in).add_backpack_to_cart()
    checkout = CheckoutPage(logged_in)
    checkout.open_cart()
    checkout.start_checkout()
    checkout.fill_details("Test", "User", "14260")
    checkout.finish()
    assert "Thank you" in checkout.confirmation_text()


@risk("product_catalog")         # score 12
def test_catalog_lists_products(logged_in):
    inv = InventoryPage(logged_in)
    assert inv.item_count() == 6
    assert "Sauce Labs Backpack" in inv.product_names()


@risk("cart_management")         # score 9
def test_add_and_remove_from_cart(logged_in):
    inv = InventoryPage(logged_in)
    inv.add_backpack_to_cart()
    assert inv.cart_count() == 1
    inv.remove_backpack_from_cart()
    assert inv.cart_count() == 0


@risk("static_content")          # score 2
def test_footer_present(logged_in):
    assert InventoryPage(logged_in).is_visible(".footer")
