from typing import Literal
from playwright.sync_api import Page


def _get_browser_state(page: Page, wait: bool = False) -> str:
    if wait:
        page.wait_for_timeout(1000)

    return page.content()


def go_to(page: Page, url: str) -> None:
    page.goto(url)
    return _get_browser_state(page)


def click(page: Page, selector: str) -> None:
    page.click(selector)
    return _get_browser_state(page)


def scroll(page: Page, direction: Literal["down", "up"] = "down") -> None:
    if direction == "down":
        page.evaluate("window.scrollBy(0, window.innerHeight);")
    elif direction == "up":
        page.evaluate("window.scrollBy(0, -window.innerHeight);")
    return _get_browser_state(page)


def hover(page: Page, selector: str) -> None:
    """
    Hovers the mouse over the element specified by the selector.
    """
    page.hover(selector)
    return _get_browser_state(page)


def rclick(page: Page, selector: str) -> None:
    """
    Right-clicks (context click) on the element specified by the selector.
    """
    page.click(selector, button="right")
    return _get_browser_state(page)


def double_click(page: Page, selector: str) -> None:
    """
    Double-clicks on the element specified by the selector.
    """
    page.dblclick(selector)
    return _get_browser_state(page)


def type_text(
    page: Page,
    selector: str,
    text: str,
    clear_first: bool = True,
    delay: int = 0,
) -> None:
    if clear_first:
        page.fill(selector, "")
    page.type(selector, text, delay=delay)
    return _get_browser_state(page)
