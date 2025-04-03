# Conversation History Tool

from datetime import datetime
from langchain.tools import Tool
from utils import conversation_history



def get_conversation_history(thread_id: str, limit: int = 10) -> str:
    """Retrieve the conversation history for a thread."""
    if thread_id not in conversation_history:
        return "No conversation history found for this thread."

    history = conversation_history[thread_id][-limit:]
    result = "Conversation History:\n\n"

    for entry in history:
        timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M:%S")
        result += f"[{timestamp}] {entry['role']}: {entry['content']}\n\n"

    return result


conversation_tool = Tool(
    name="conversation_history",
    func=get_conversation_history,
    description="""
        Use this tool to retrieve the recent conversation history when needed.
        Input should be a thread_id (default: current thread) and optional limit parameter.
        Example: {"thread_id": "unique_thread_1", "limit": 5}
        Use this when you need to reference or summarize previous exchanges.
        """,
)