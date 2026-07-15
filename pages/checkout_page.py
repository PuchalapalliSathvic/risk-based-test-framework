"""Page Object for the checkout / payment flow."""
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    CART_LINK = ".shopping_cart_link"
    CHECKOUT_BTN = "[data-test='checkout']"
    FIRST_NAME = "[data-test='firstName']"
    LAST_NAME = "[data-test='lastName']"
    POSTAL = "[data-test='postalCode']"
    CONTINUE = "[data-test='continue']"
    FINISH = "[data-test='finish']"
    TOTAL = ".summary_total_label"
    COMPLETE_HEADER = ".complete-header"

    def open_cart(self):
        self.page.click(self.CART_LINK)
        return self

    def start_checkout(self):
        self.page.click(self.CHECKOUT_BTN)
        return self

    def fill_details(self, first, last, postal):
        self.page.fill(self.FIRST_NAME, first)
        self.page.fill(self.LAST_NAME, last)
        self.page.fill(self.POSTAL, postal)
        self.page.click(self.CONTINUE)
        return self

    def order_total(self):
        return self.text_of(self.TOTAL)

    def finish(self):
        self.page.click(self.FINISH)
        return self

    def confirmation_text(self):
        return self.text_of(self.COMPLETE_HEADER)
