from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright
import os
import dspy
import weave
import actions
from custom_react import ReActTruncated
import utils

lm = dspy.LM(
    "anthropic/claude-3-7-sonnet-latest",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    thinking={"type": "enabled", "budget_tokens": 10000},
    temperature=1,
    max_tokens=64000,
)
dspy.configure(lm=lm)
weave.init(os.getenv("WANDB_PROJECT_NAME"))

blacklist = ["https://google.com", "https://www.google.com"]


class ResultSchema(BaseModel):
    new_state: str = Field(description="The new state of the page after the action.")
    result: Literal["success", "failure"] = Field(
        description="The result of the action."
    )
    error: str | None = Field(
        description="The error message if the action failed, otherwise None."
    )


class BrowserAgent(dspy.Signature):
    """
    You are a helpful browser agent that has access to a browser.
    You will be given a task to complete and a list of available tools.
    Your goal is to complete the task using the available tools.
    """

    task: str = dspy.InputField()
    answer: str = dspy.OutputField()


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        run_id = str(datetime.now().timestamp())  # mlflow.active_run()

        os.makedirs(f"frames/{run_id}", exist_ok=True)
        frame_counter = {"count": 0}

        def save_frame(page, action_name, extra_info=""):
            frame_counter["count"] += 1
            filename = f"{frame_counter['count']:03d}_{action_name}"
            if extra_info:
                filename += f"_{extra_info}"
            filename += ".png"
            path = os.path.join(f"frames/{run_id}", filename)
            page.screenshot(path=path, full_page=False)
            return path

        def go_to(url: str) -> ResultSchema:
            """Navigates to the specified URL."""
            if any(b in url for b in blacklist):
                return {
                    "new_state": page.content(),
                    "result": "failure",
                    "error": "Blacklisted URL",
                }
            new_state = actions.go_to(page, url)
            ss_info = url.replace("https://", "").replace("/", "_")
            save_frame(page, "go_to", extra_info=ss_info)
            return {"new_state": new_state, "result": "success"}

        def click(selector: str) -> ResultSchema:
            """Clicks on the element specified by the selector."""
            new_state = actions.click(page, selector)
            ss_info = selector.replace("#", "id_").replace(".", "cls_")
            save_frame(page, "click", extra_info=ss_info)
            return {"new_state": new_state, "result": "success"}

        def type_text(selector: str, text: str, submit: bool = False) -> ResultSchema:
            """Types the given text into the element specified by the selector. If submit is True, the text will be submitted by pressing enter."""
            new_state = actions.type_text(page, selector, text, True)
            ss_info = selector.replace("#", "id_").replace(".", "cls_")
            save_frame(page, "type_text", extra_info=ss_info)

            if submit:
                new_state = actions.submit(page)
                save_frame(page, "submit", extra_info=ss_info)
                return {"new_state": new_state, "result": "success"}

            return {"new_state": new_state, "result": "success"}

        def scroll(direction: Literal["up", "down"]) -> ResultSchema:
            """Scrolls the page up or down."""
            new_state = actions.scroll(page, direction)
            save_frame(page, "scroll", extra_info=direction)
            return {"new_state": new_state, "result": "success"}

        def go_back() -> ResultSchema:
            """Navigates back to the previous page."""
            new_state = actions.go_back(page)
            save_frame(page, "go_back")
            return {"new_state": new_state, "result": "success"}

        react = ReActTruncated(
            BrowserAgent,
            tools=[go_to, click, type_text, scroll, go_back],
            max_iters=20,
        )
        answer = react(
            task="Go to arxiv and find the top 3 papers regarding browser automation benchmarks."
        )
        print(answer)

        # After finishing, join all frames as a gif (or video if preferred)
        utils.create_gif(run_id)
