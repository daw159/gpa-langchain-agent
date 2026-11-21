
import asyncio
import os
import streamlit as st

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from llm import llm
from agent import SYSTEM_PROMPT

load_dotenv()

MCP_URL = "https://gpa-agent-server.onrender.com/mcp"

st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 AI Student Assistant")
st.caption("GPA & CGPA Assistant powered by LangChain + MCP")

# Sidebar
with st.sidebar:
    st.header("Student")

    student = st.text_input(
        "Student name",
        value="dawo"
    ).strip().lower()

    if not student:
        st.warning("Enter a student name.")
        st.stop()

    if st.button("Clear Conversation"):
        async def clear_chat():
            async with AsyncSqliteSaver.from_conn_string(
                "chats.db"
            ) as memory:
                await memory.adelete_thread(student)

        asyncio.run(clear_chat())
        st.rerun()


async def get_history():
    async with AsyncSqliteSaver.from_conn_string(
        "chats.db"
    ) as memory:

        config = {
            "configurable": {
                "thread_id": student
            }
        }

        state = await memory.aget_tuple(config)

        if state is None:
            return []

        messages = state.checkpoint.get(
            "channel_values", {}
        ).get("messages", [])

        return [
            (msg.type, msg.text)
            for msg in messages
            if msg.type in ("human", "ai") and msg.text
        ]


# Display saved messages
for role, content in asyncio.run(get_history()):
    with st.chat_message(
        "user" if role == "human" else "assistant"
    ):
        st.write(content)


# User message
prompt = st.chat_input("Ask about your GPA or CGPA...")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        async def run_agent():
            full_response = ""

            async with MCPAdapter(MCP_URL) as adapter:
                tools = await adapter.list_tools()

                async with AsyncSqliteSaver.from_conn_string(
                    "chats.db"
                ) as memory:

                    agent = create_agent(
                        model=llm,
                        tools=tools,
                        system_prompt=SYSTEM_PROMPT,
                        checkpointer=memory
                    )

                    config = {
                        "configurable": {
                            "thread_id": student
                        }
                    }

                    async for chunk in agent.astream(
                        {
                            "messages": [
                                HumanMessage(content=prompt)
                            ]
                        },
                        config,
                        stream_mode=["messages"],
                        version="v2"
                    ):
                        if chunk["type"] == "messages":
                            token, metadata = chunk["data"]

                            if (
                                metadata.get("langgraph_node") == "model"
                                and token.text
                            ):
                                full_response += token.text
                                placeholder.markdown(full_response + "▌")

                    placeholder.markdown(full_response)

        try:
            asyncio.run(run_agent())
        except Exception as e:
            st.error(f"Error: {e}")
