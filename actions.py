from playwright.sync_api import Page


def _get_browser_state(page: Page, wait: bool = False) -> str:
    if wait:
        page.wait_for_timeout(1000)
    return page.content()


def click(page: Page, selector: str) -> None:
    """
    Clicks on the element specified by the selector.
    """
    page.click(selector)
    return _get_browser_state(page)


def scroll(page: Page, x: int = 0, y: int = 0) -> None:
    """
    Scrolls the page to the specified x, y coordinates.
    """
    page.evaluate(f"window.scrollTo({x}, {y});")
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
    """
    Types the given text into the element specified by the selector.
    Optionally clears the field first and sets a delay between keystrokes.
    """
    if clear_first:
        page.fill(selector, "")
    page.type(selector, text, delay=delay)
    return _get_browser_state(page)


def go_to(page: Page, url: str) -> None:
    """
    Navigates the page to the specified URL.
    """
    page.goto(url)
    return _get_browser_state(page)
