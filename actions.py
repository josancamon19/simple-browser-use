from playwright.sync_api import Page, BrowserContext


def click(page: "Page", selector: str) -> None:
    """
    Clicks on the element specified by the selector.
    """
    page.click(selector)


def scroll(page: "Page", x: int = 0, y: int = 0) -> None:
    """
    Scrolls the page to the specified x, y coordinates.
    """
    page.evaluate(f"window.scrollTo({x}, {y});")


def hover(page: "Page", selector: str) -> None:
    """
    Hovers the mouse over the element specified by the selector.
    """
    page.hover(selector)


def rclick(page: "Page", selector: str) -> None:
    """
    Right-clicks (context click) on the element specified by the selector.
    """
    page.click(selector, button="right")


def double_click(page: "Page", selector: str) -> None:
    """
    Double-clicks on the element specified by the selector.
    """
    page.dblclick(selector)


def type_text(
    page: "Page",
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


def go_to(page: "Page", url: str) -> None:
    """
    Navigates the page to the specified URL.
    """
    page.goto(url)


def switch_tab(context: "BrowserContext", tab_index: int) -> "Page":
    """
    Switches to the tab (page) at the given index in the browser context.
    Returns the page object for the new tab.
    """
    pages = context.pages
    if 0 <= tab_index < len(pages):
        return pages[tab_index]
    else:
        raise IndexError("Tab index out of range.")


def list_tabs(context: "BrowserContext") -> list:
    """
    Returns a list of URLs for all open tabs (pages) in the browser context.
    """
    return [page.url for page in context.pages]
