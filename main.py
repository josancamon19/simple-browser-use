import os
from typing import Literal
from playwright.sync_api import sync_playwright
import dspy
import actions

lm = dspy.LM(
    "anthropic/claude-3-7-sonnet-latest", api_key=os.getenv("ANTHROPIC_API_KEY")
)
dspy.configure(lm=lm)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def go_to(url: str):
            """Navigates to the specified URL."""
            return actions.go_to(page, url)

        def click(selector: str):
            """Clicks on the element specified by the selector."""
            return actions.click(page, selector)

        def type_text(selector: str, text: str):
            """Types the given text into the element specified by the selector."""
            return actions.type_text(page, selector, text)

        def scroll(direction: Literal["up", "down"]):
            """Scrolls the page up or down."""
            return actions.scroll(page, direction)

        instructions = "Navigate seamlessly between pages, clicking and typing as needed to complete the task."
        signature = dspy.Signature("task: str -> result: str", instructions)
        react = dspy.ReAct(
            signature,
            tools=[go_to, click, type_text, scroll],
            max_iters=20,
        )
        answer = react(
            task="Go to wikipedia.org, find the top article of the day, navigate to it, and find the latest editor name."
        )
        print(answer)
