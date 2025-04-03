# Enhanced Website Crawling with Error Handling

import asyncio
import json
from datetime import datetime
from typing import Dict
from crawl4ai import AsyncWebCrawler
from langchain.tools import Tool
import json


async def _crawl(url: str, max_depth: int = 1, max_links: int = 10) -> Dict[str, Any]:
    """Asynchronous crawling with configurable depth and link limit."""
    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(
                url=url, max_depth=max_depth, max_links=max_links, timeout=30
            )
            return {
                "markdown": result.markdown,
                "links": result.links,
                "images": result.media.get("images", [])
                # "status_code": result.status_code,
                # "error": None,
            }
        except Exception as e:
            return {"markdown": "", "links": [], "status_code": None, "error": str(e)}


def crawl_website(url: str, params: str = "") -> str:
    """
    Crawls the provided URL using AsyncWebCrawler from crawl4ai
    and returns the markdown content with additional parameters.

    Args:
        url: The URL to crawl (must start with http:// or https://)
        params: Optional JSON string with parameters like {"max_depth": 2, "max_links": 15}
    """
    # Validate URL
    if not (url.startswith("http://") or url.startswith("https://")):
        return "Error: URL must start with http:// or https://"

    # Parse parameters if provided
    config = {"max_depth": 1, "max_links": 10}
    if params:
        try:
            user_config = json.loads(params)
            config.update(user_config)
        except json.JSONDecodeError:
            pass  # Use defaults if JSON parsing fails

    # Run the crawler
    result = asyncio.run(
        _crawl(url, max_depth=config["max_depth"], max_links=config["max_links"])
    )

    if result["error"]:
        return f"Error crawling {url}: {result['error']}"

    # Return information about the crawl along with the content
    return f"""
URL: {url}
Images: {result['images']}
Links found: {len(result['links'])}
CONTENT:
{result['markdown']}
"""


crawl_tool = Tool(
    name="crawl_website",
    func=crawl_website,
    description=f"""
        Use this tool to thoroughly analyze web content. The tool will crawl the website and extract content.

        Input format:
          - Simple: Just provide a valid URL starting with http:// or https://
          - Advanced: JSON with URL and parameters: {{"url": "https://example.com", "params": {{"max_depth": 2, "max_links": 15}}}}

        Features:
          - Automatically extracts text content
          - Can follow links to specified depth
          - Reports number of links found
          - Shows HTTP status code

        Use when:
          - You need detailed information from a specific website
          - You want to extract structured content
          - You need to verify or cross-reference information
          - You need to collect image urls

        Current date: {datetime.now().strftime('%Y-%m-%d')}
        """,
)