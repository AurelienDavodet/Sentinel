import os
import time
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
import vertexai
from langchain.chat_models import init_chat_model
from langchain.chat_models import init_chat_model
from tools import conversation_tool, summarize_tool, crawl_tool, search_tool
from utils import save_conversation



PROJECT_ID = "sopra-ai-hackathon-renault"  # @param {type: "string", placeholder: "[your-project-id]", isTemplate: true}
if not PROJECT_ID or PROJECT_ID == "sopra-ai-hackathon-renault":
    PROJECT_ID = str(os.environ.get("GOOGLE_CLOUD_PROJECT"))

LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

MODEL_NAME = "gemini-2.0-flash"

client = init_chat_model(MODEL_NAME, model_provider="google_vertexai")

# client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

memory = MemorySaver()

# Combine Tools
tools = [search_tool, crawl_tool, conversation_tool, summarize_tool]

# Create the agent with all tools
agent = create_react_agent(client, tools, checkpointer=memory)


# ---------------------------------------------------------------------------
# Enhanced Agent Usage Function
# ---------------------------------------------------------------------------

import mesop as me
import mesop.labs as mel
from langchain_core.messages import HumanMessage

# Assuming agent, process_agent_response, and save_conversation are already defined

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

me.colab_show(path="/chat")
