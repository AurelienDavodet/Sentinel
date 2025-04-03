import os
from datetime import datetime
from typing import Any, Dict, List, Union

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from utils import constants

load_dotenv()


def get_openai_client(model):
    """Initialize and return the OpenAI Chat client."""
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo",
        temperature=0.7,
    )


# Initialize client and memory
client = get_openai_client(model=constants.MODEL_NAME)

# Create a conversation history store
conversation_history: Dict[str, List[Dict[str, Union[str, Any]]]] = {}


def save_conversation(thread_id: str, role: str, message: str) -> None:
    """Save a message to the conversation history."""
    if thread_id not in conversation_history:
        conversation_history[thread_id] = []

    conversation_history[thread_id].append(
        {"role": role, "content": message, "timestamp": datetime.now().isoformat()}
    )


def process_agent_response(step, thread_id):
    """Process and display agent responses with better formatting."""
    if "agent" in step and "messages" in step["agent"] and step["agent"]["messages"]:
        content = step["agent"]["messages"][0]
        if hasattr(content, "content") and content.content != "":
            print("\n🤖 Agent:")
            print("-" * 80)
            print(content.content)
            print("-" * 80)

            # Save to conversation history
            save_conversation(thread_id, "Agent", content.content)

            return content.content
        else:
            tool_calls = content.additional_kwargs.get("tool_calls", [])
            if tool_calls:
                tool_name = tool_calls[0]["function"]["name"]
                print(f"\n🔧 Using tool: {tool_name}")
                print("-" * 80)

                return f"Using tool: {tool_name}"

    elif "tools" in step and "messages" in step["tools"] and step["tools"]["messages"]:
        content = step["tools"]["messages"][0]
        if hasattr(content, "content"):
            print("\n🔍 Tool Result:")
            print("-" * 80)
            print(content.content[:500] + ("..." if len(content.content) > 500 else ""))
            print("-" * 80)

            return content.content

    return None
