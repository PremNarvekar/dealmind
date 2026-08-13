"""
MarketAgent — researches market size, competitors, and recent news.

Uses create_agent() from langchain which returns a CompiledStateGraph.
The agent's output schema includes:
  - messages: list[AnyMessage]  (the conversation history)
  - structured_response: MarketResult  (the parsed Pydantic result)

The supervisor graph calls this agent as a subgraph node.
"""
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from tools.market_tools import (
    search_market_size,
    search_competitors,
    search_recent_news,
)
from models.memo import MarketResult


MARKET_SYSTEM_PROMPT = """
You are a top-tier market research analyst.
Your job is to gather comprehensive information about the market for a given company.
You must use your tools to find the market size, competitors, and recent news.
Do not guess. Use the tools.

YOUR FINAL OUTPUT MUST BE A RAW JSON OBJECT with the following schema:
{
  "market_size": "string",
  "competitors": ["string", "string"],
  "recent_news": ["string", "string"],
  "summary": "string"
}
Ensure the output is ONLY the JSON object, with no markdown formatting or extra text.
"""

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0, max_retries=6)

market_agent = create_agent(
    model=llm,
    tools=[
        search_market_size,
        search_competitors,
        search_recent_news,
    ],
    system_prompt=MARKET_SYSTEM_PROMPT,
    name="market_agent",
)