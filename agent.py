
import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from llm import llm

load_dotenv()

MCP_URL = os.getenv(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp"
)

# KEEP YOUR COMPLETE EXISTING SYSTEM_PROMPT HERE
SYSTEM_PROMPT = '''You are the AI agent that helps students with GPA and CGPA questions. You will never do math yourself. Every number must come from a tool. You only decide which tool to use, then explain the result in simple, natural words.

If you don't have the marks, credit hours, semester number, GPA, or CGPA info, then ask the student for it. Never guess or make up a number. Ask for only one or two missing things at a time, not everything at once.

MD-001 and MD-002 are Math Deficiency courses, pass/fail only. They have no credit hours and are not included in GPA. Every other course counts, including Quran Translation, which is always 0.5 credit hours and is included in the GPA calculation.

When a student gives you their current or upcoming semester number and wants a target CGPA plan, remaining credit hours must include that semester itself, not just the semesters after it. get_remaining_credit_hours(N) only returns hours after semester N. So if the student is about to start or is currently in semester X, call get_remaining_credit_hours(X - 1) to get the total including semester X, not get_remaining_credit_hours(X).

A required GPA above 4.0 is impossible, so never report it as the final answer. Instead check further ahead one semester at a time. First find the required GPA using only the student's current semester's credit hours. If that is above 4.0, add the next semester's credit hours and check again. Keep adding one semester at a time, up to semester 8, until the required GPA is 4.0 or below. Then tell the student that GPA and how many semesters it covers. If even including every remaining semester the required GPA is still above 4.0, tell the student plainly the target is not reachable, and tell them the best CGPA they could reach if every remaining semester was a perfect 4.0.

To find how many credit hours a semester has, call get_semester_courses for that semester and add up its course credits yourself. Do not ask the student for standard semester credit hours, only for their personal CGPA and completed credit hours. When checking horizons, stop and report the first horizon where the required GPA is 4.0 or below. Do not skip ahead to counting all remaining semesters.

Once you have given a real result or a semester GPA, a new CGPA, or a target plan, then you can offer to save it. Never offer just after a question or a course lookup, and never save without the student saying yes.

You don't help with repeating or improving a course, curves or relative grading, incomplete/withdrawn/frozen grades. If asked, just say you can't help with that.

You can remember previous messages within the same conversation thread, but not after the program restarts when using InMemorySaver.

Do not show your calculations, formulas, or arithmetic in your reply. Only call the tools and state the final result in words.

Use tavily_web_search to find study resources when requested.
Send phone notifications only when the student explicitly asks.
Use send_notification for this.
Never claim a notification succeeded if the tool reports an error.

Call only tools supplied in the tools list, using their exact names.
Never invent a tool name. "commentary" is not a tool.

Talk like a friendly student. Use short, clear sentences, simple words. Don't show your tool calls, just give the final answer.'''



def choose_student():
    while True:
        name = input("\nWho is chatting? ").strip().lower()

        if name:
            return name

        print("Please enter a name.")


async def show_threads(memory):
    thread_ids = set()

    async for checkpoint in memory.alist(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]
        thread_ids.add(thread_id)

    print(
        "Saved chats:",
        ", ".join(sorted(thread_ids)) or "None"
    )


async def show_history(agent, config):
    state = await agent.aget_state(config)

    if not state.values:
        print("No conversation history.")
        return

    for message in state.values.get("messages", []):
        role = message.type

        if role == "human":
            print("You:", message.text)

        elif role == "ai":
            if message.text:
                print("Agent:", message.text)


async def forget_student(memory, student):
    # Delete all saved checkpoints for this thread
    await memory.adelete_thread(student)

    print(f"Conversation for '{student}' deleted.")



async def main():

    print("=== AI Student Assistant ===")
    print("Connecting to MCP server...")

    async with MCPAdapter(MCP_URL) as adapter:

        tools = await adapter.list_tools()

        print(f"Connected! Found {len(tools)} MCP tools.")

        # Persistent asynchronous SQLite memory
        async with AsyncSqliteSaver.from_conn_string(
            "chats.db"
        ) as memory:

            agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                checkpointer=memory
            )

            print(
                "\nCommands: /switch, /threads, "
                "/history, /forget, /exit"
            )

            student = choose_student()

            while True:

                config = {
                    "configurable": {
                        "thread_id": student
                    }
                }

                user_input = input(
                    f"\n[{student}] You: "
                ).strip()

                if not user_input:
                    continue

                command = user_input.lower()

                if command == "/exit":
                    print("Goodbye!")
                    break

                if command == "/switch":
                    student = choose_student()
                    continue

                if command == "/threads":
                    await show_threads(memory)
                    continue

                if command == "/history":
                    await show_history(agent, config)
                    continue

                if command == "/forget":
                    confirm = input(
                        f"Delete all history for {student}? "
                        "(yes/no): "
                    ).strip().lower()

                    if confirm == "yes":
                        await forget_student(memory, student)
                    else:
                        print("Cancelled.")

                    continue

                # Task 4: Async streaming
                try:
                    print("\nAgent: ", end="", flush=True)

                    async for chunk in agent.astream(
                        {
                            "messages": [
                                HumanMessage(content=user_input)
                            ]
                        },
                        config,
                        stream_mode=["updates", "messages"],
                        version="v2"
                    ):

                        if chunk["type"] == "messages":

                            token, metadata = chunk["data"]
                            node = metadata.get("langgraph_node")

                            if node == "model" and token.text:
                                print(
                                    token.text,
                                    end="",
                                    flush=True
                                )

                        elif chunk["type"] == "updates":

                            for node, update in chunk["data"].items():

                                if node == "model":

                                    for message in update.get(
                                        "messages", []
                                    ):

                                        for tool_call in getattr(
                                            message,
                                            "tool_calls",
                                            []
                                        ):
                                            print(
                                                f"\n[Calling tool: "
                                                f"{tool_call['name']}]",
                                                flush=True
                                            )

                                elif node == "tools":

                                    for message in update.get(
                                        "messages", []
                                    ):
                                        print(
                                            f"\n[Tool completed: "
                                            f"{message.name}]",
                                            flush=True
                                        )

                    print()

                except Exception as e:
                    print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())


