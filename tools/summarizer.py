# Summarization Tool

from langchain.tools import Tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def create_summarizer():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
         You are an expert summarizer. Create a concise summary of the provided text.
         Focus on key points, main arguments, and important details.
         Organize the summary in a structured format with appropriate headings.
         """,
            ),
            ("human", "{text}"),
        ]
    )

    return prompt | client | StrOutputParser()

summarizer = create_summarizer()


def summarize_text(text: str) -> str:
    """Summarize long text content."""
    if len(text) < 500:
        return "The provided text is too short to require summarization."

    try:
        summary = summarizer.invoke({"text": text})
        return summary
    except Exception as e:
        return f"Error during summarization: {str(e)}"


summarize_tool = Tool(
    name="summarize",
    func=summarize_text,
    description="""
        Use this tool to create a concise, structured summary of long text content.
        Provide the text you want summarized as input.
        Best used for:
        - Long search results
        - Webpage content
        - Previous conversation segments
        - Any text that needs condensation while preserving key information
        """,
)