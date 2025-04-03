import mesop as me
import mesop.labs as mel
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from tools import conversation_tool, crawl_tool, search_tool, summarize_tool
from utils import client, process_agent_response, save_conversation

memory = MemorySaver()

# Combine Tools
tools = [search_tool, crawl_tool, conversation_tool, summarize_tool]

# Create the agent with all tools
agent = create_react_agent(client, tools, checkpointer=memory)


# Web page
def transform(prompt: str, history: list[mel.ChatMessage]) -> str:
    thread_id = "mesop_chat_thread"

    # Save user message
    save_conversation(thread_id, "User", prompt)

    config = {"configurable": {"thread_id": thread_id}}
    final_response = ""

    try:
        for step in agent.stream(
            {"messages": [HumanMessage(content=prompt)]},
            config,
            stream_mode="updates",
        ):
            response = process_agent_response(step, thread_id)
            if response and "agent" in step:
                final_response = response

    except Exception as e:
        final_response = f"Error during agent processing: {str(e)}"

    return final_response


@me.page(path="/chat")
def chat():
    mel.chat(transform)
