import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import dspy

server_params = StdioServerParameters(
    command="npx", args=["@playwright/mcp@latest", "-v"], env=None
)

lm = dspy.LM(
    "anthropic/claude-3-7-sonnet-latest",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    thinking={"type": "enabled", "budget_tokens": 10000},
    temperature=1,
    max_tokens=64000,
)
dspy.configure(lm=lm)


class BrowserAgent(dspy.Signature):
    """
    You are a browser agent that has access to a browser.
    You will be given a task to complete, you will need to use the tools provided to complete this task.
    """

    task: str = dspy.InputField()
    answer: str = dspy.OutputField()


async def run(task: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()

            dspy_tools = []
            for tool in tools.tools:
                dspy_tools.append(dspy.Tool.from_mcp_tool(session, tool))

            react = dspy.ReAct(BrowserAgent, tools=dspy_tools)

            result = await react.acall(task=task)
            print(result.answer)


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        run(
            "Go to arxiv and find the top 3 papers regarding browser automation benchmarks."
        )
    )
