# DuckDuckGo Search with Improved Error Handling

from langchain_community.tools import DuckDuckGoSearchRun
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain.tools import Tool
from datetime import datetime

duckduckgo_search_tool = DuckDuckGoSearchRun()


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    reraise=True,
)
def duckduckgo_search_with_retry(query: str) -> str:
    """
    Wraps the DuckDuckGo search call with exponential backoff retry.
    Uses tenacity for more robust retry handling.
    """
    try:
        duckduck_result = duckduckgo_search_tool.invoke(query)
        return duckduck_result
    except Exception as e:
        print(f"Error during DuckDuckGo search: {str(e)}")
        if "RatelimitException" in str(e):
            # This will trigger the retry
            raise e
        return (
            f"Search failed with error: {str(e)}. Please try a different query or tool."
        )


search_tool = Tool(
    name="DuckDuckGoSearch",
    func=duckduckgo_search_with_retry,
    description="""
        Use this tool when you need current or updated information that you don't already have.
        Use it multiple times as needed to get comprehensive information.
        
        Best practices:
        1. First try to answer using your existing knowledge
        2. Use specific, focused search queries
        3. Break complex queries into simple, targeted searches
        4. Use quotes for exact phrase matching
        
        Avoid using this tool for:
        - Basic factual information you should already know
        - Historical information before 2024
        - Definition of common terms
        
        Current date: {current_date}
        """.format(
        current_date=datetime.now().strftime("%Y-%m-%d")
    ),
)