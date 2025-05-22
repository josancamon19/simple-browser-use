from typing import Literal
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import time
import re

from browser_state import get_browser_state


def _get_browser_state(
    page: Page, wait: bool = False, max_attempts: int = 5, delay: float = 0.2
) -> dict:
    if wait:
        page.wait_for_timeout(1000)

    last_exc = None
    for _ in range(max_attempts):
        try:
            return {
                "snapshot": get_browser_state(page),
                "url": page.url,
                "title": page.title(),
            }
        except Exception as e:
            last_exc = e
            time.sleep(delay)
    raise RuntimeError(
        f"Failed to get browser state after {max_attempts} attempts: {last_exc}"
    )


def _ref_to_selector(ref: str) -> str:
    """
    Converts a [ref=...] string to a CSS attribute selector.
    E.g. [ref=e8] -> [ref="e8"]
    """
    # If already a valid CSS selector, return as is
    if ref.startswith("[ref="):
        # Extract the value inside [ref=...]
        m = re.match(r"\[ref=['\"]?([^\]'\"]+)['\"]?\]", ref)
        if m:
            value = m.group(1)
            return f'[ref="{value}"]'
        return ref
    # If not a [ref=...] string, treat as a CSS selector and add brackets if needed
    # If the selector looks like a bare word (e.g. e16), treat as [ref="e16"]
    if re.match(r"^[a-zA-Z0-9_\-]+$", ref):
        return f'[ref="{ref}"]'
    return ref


def go_to(page: Page, url: str) -> dict:
    page.goto(url, wait_until="domcontentloaded")
    return _get_browser_state(page, wait=True)


def go_back(page: Page) -> dict:
    page.go_back(wait_until="domcontentloaded")
    return _get_browser_state(page, wait=True)


def click(page: Page, selector: str) -> dict:
    selector = _ref_to_selector(selector)
    try:
        page.wait_for_selector(selector, state="visible", timeout=5000)
        page.click(selector, timeout=5000)
    except PlaywrightTimeoutError as e:
        raise ValueError(
            f"TimeoutError: click Could not find or interact with selector '{selector}': {e}"
        )
    except Exception as e:
        raise ValueError(f"Exception during click for selector '{selector}': {e}")
    # Wait for possible navigation or DOM update
    return _get_browser_state(page, wait=True)


def scroll(page: Page, direction: Literal["down", "up"] = "down") -> dict:
    if direction == "down":
        page.evaluate("window.scrollBy(0, window.innerHeight);")
    elif direction == "up":
        page.evaluate("window.scrollBy(0, -window.innerHeight);")
    return _get_browser_state(page, wait=True)


def type_text(
    page: Page,
    selector: str,
    text: str,
    clear_first: bool = True,
    delay: int = 0,
) -> dict:
    """
    Types text into the element specified by the selector or [ref=...] reference.
    If selector is a [ref=...] string, converts to attribute selector.
    If selector is a bare word (e.g. e16), treats as [ref="e16"].
    """
    selector = _ref_to_selector(selector)
    try:
        page.wait_for_selector(selector, state="visible", timeout=5000)
        if clear_first:
            page.fill(selector, "")
        page.type(selector, text, delay=delay)
    except PlaywrightTimeoutError as e:
        raise ValueError(
            f"TimeoutError: type_text Could not find or interact with selector '{selector}': {e}"
        )
    except Exception as e:
        raise ValueError(f"Exception during type_text for selector '{selector}': {e}")
    return _get_browser_state(page, wait=True)


def submit(page: Page) -> dict:
    page.keyboard.press("Enter")
    # Wait for possible navigation or DOM update after submit
    return _get_browser_state(page, wait=True)
