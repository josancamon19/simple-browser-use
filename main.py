import os
from typing import Literal
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright
import dspy
import actions
import os
import base64
import mlflow

from custom_react import ReActTruncated


LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = (
    "https://us.cloud.langfuse.com/api/public/otel/v1/traces"
)
os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
os.environ["OTEL_EXPORTER_OTLP_TRACES_PROTOCOL"] = "http/protobuf"

lm = dspy.LM(
    "anthropic/claude-3-7-sonnet-latest", api_key=os.getenv("ANTHROPIC_API_KEY")
)
dspy.configure(lm=lm)
mlflow.dspy.autolog()


class ResultSchema(BaseModel):
    new_state: str = Field(description="The new state of the page after the action.")
    result: Literal["success", "failure"] = Field(
        description="The result of the action."
    )


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def go_to(url: str) -> ResultSchema:
            """Navigates to the specified URL."""
            return {"new_state": actions.go_to(page, url), "result": "success"}

        def click(selector: str) -> ResultSchema:
            """Clicks on the element specified by the selector."""
            return {"new_state": actions.click(page, selector), "result": "success"}

        def type_text(selector: str, text: str) -> ResultSchema:
            """Types the given text into the element specified by the selector."""
            return {
                "new_state": actions.type_text(page, selector, text),
                "result": "success",
            }

        def scroll(direction: Literal["up", "down"]) -> ResultSchema:
            """Scrolls the page up or down."""
            return {"new_state": actions.scroll(page, direction), "result": "success"}

        def go_back() -> ResultSchema:
            """Navigates back to the previous page."""
            return {"new_state": actions.go_back(page), "result": "success"}

        instructions = "Navigate seamlessly between pages, clicking and typing as needed to complete the task."
        signature = dspy.Signature("task: str -> result: str", instructions)
        react = ReActTruncated(
            signature,
            tools=[go_to, click, type_text, scroll, go_back],
            max_iters=20,
        )
        answer = react(
            task="Go to google.com, then search servicenow research, open it, then find the papers from 2024 related to browser agents."
        )
        print(answer)
