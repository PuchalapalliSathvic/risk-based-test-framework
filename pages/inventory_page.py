"""Page Object for the product catalog + cart actions."""
from pages.base_page import BasePage


class InventoryPage(BasePage):
    ITEM = ".inventory_item"
    ITEM_NAME = ".inventory_item_name"
    ADD_BACKPACK = "[data-test='add-to-cart-sauce-labs-backpack']"
    REMOVE_BACKPACK = "[data-test='remove-sauce-labs-backpack']"
    CART_BADGE = ".shopping_cart_badge"
    CART_LINK = ".shopping_cart_link"
    SORT = "[data-test='product-sort-container']"

    def item_count(self):
        return len(self.page.query_selector_all(self.ITEM))

    def product_names(self):
        return [e.text_content() for e in self.page.query_selector_all(self.ITEM_NAME)]

    def add_backpack_to_cart(self):
        self.page.click(self.ADD_BACKPACK)
        return self

    def remove_backpack_from_cart(self):
        self.page.click(self.REMOVE_BACKPACK)
        return self

    def cart_count(self):
        if self.is_visible(self.CART_BADGE):
            return int(self.text_of(self.CART_BADGE))
        return 0

    def sort_by(self, value):
        self.page.select_option(self.SORT, value)
        return self
