"""Base page object. All page objects inherit shared navigation/helpers."""


class BasePage:
    BASE_URL = "https://www.saucedemo.com"

    def __init__(self, page):
        self.page = page

    def goto(self, path="/"):
        self.page.goto(f"{self.BASE_URL}{path}")

    def text_of(self, selector):
        return self.page.text_content(selector)

    def is_visible(self, selector):
        return self.page.is_visible(selector)
