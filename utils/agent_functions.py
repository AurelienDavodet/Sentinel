import time
from langchain_core.messages import HumanMessage
from utils import save_conversation
from datetime import datetime
from typing import Dict, List, Any, Union

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


def _run_agent_conversation(query: str, thread_id: str = "default_thread"):
    """
    Run a conversation with the agent and display the results in a more user-friendly way.

    Args:
        query: The user's question or message
        thread_id: A unique identifier for the conversation thread
    """
    print(f"\n💬 User: {query}")
    print("-" * 80)

    # Save user message to history
    save_conversation(thread_id, "User", query)

    config = {"configurable": {"thread_id": thread_id}}
    final_response = None

    try:
        for step in agent.stream(
            {"messages": [HumanMessage(content=query)]}, config, stream_mode="updates"
        ):
            response = process_agent_response(step, thread_id)
            if response and "agent" in step:
                final_response = response

    except Exception as e:
        error_message = f"Error during agent processing: {str(e)}"
        print(f"\n❌ {error_message}")
        final_response = error_message

    return final_response


# ---------------------------------------------------------------------------
# Interactive Agent with Continuous Conversation
# ---------------------------------------------------------------------------

def interactive_agent():
    """Run an interactive conversation with the agent."""
    thread_id = f"thread_{int(time.time())}"
    print("\n📱 Interactive Agent - Type 'exit' to quit\n")

    while True:
        query = input("\n❓ What would you like to know? ")
        if query.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the agent. Goodbye!")
            break

        _run_agent_conversation(query, thread_id)
