"""Page Object for the SauceDemo login page (authentication risk area)."""
from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = "#user-name"
    PASSWORD = "#password"
    LOGIN_BTN = "#login-button"
    ERROR = "[data-test='error']"

    def open(self):
        self.goto("/")
        return self

    def login(self, username, password):
        self.page.fill(self.USERNAME, username)
        self.page.fill(self.PASSWORD, password)
        self.page.click(self.LOGIN_BTN)
        return self

    def error_message(self):
        if self.is_visible(self.ERROR):
            return self.text_of(self.ERROR)
        return None

    def is_logged_in(self):
        return "/inventory.html" in self.page.url
