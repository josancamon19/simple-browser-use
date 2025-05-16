from playwright.sync_api import sync_playwright
import json


def observe_environment(
    url,
    save_accessibility_tree=False,
    save_dom=False,
    take_screenshot=False,
    accessibility_tree_filename="accessibility_tree.json",
    dom_filename="dom.html",
    screenshot_filename="screenshot.png",
):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        # Extract the accessibility snapshot
        snapshot = page.accessibility.snapshot()

        if save_accessibility_tree:
            with open(accessibility_tree_filename, "w") as f:
                json.dump(snapshot, f, indent=2)

        if save_dom:
            dom_content = page.content()
            with open(dom_filename, "w", encoding="utf-8") as f:
                f.write(dom_content)

        if take_screenshot:
            page.screenshot(path=screenshot_filename)

        browser.close()


# Example usage
observe_environment(
    "https://en.wikipedia.org/wiki/Biophysics",
    save_accessibility_tree=True,
    save_dom=True,
    take_screenshot=True,
)
