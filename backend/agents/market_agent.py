from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.market_tools import (
    search_market_size,
    search_competitors,
    search_recent_news,
)

from models.memo import MarketResult


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
)


SYSTEM_PROMPT = """
You are the Market Research Agent for an investment analysis system.

Your responsibility is ONLY to research:

- market size
- competitors
- recent relevant news
- industry growth and trends

Do not research founders, team backgrounds, or technical implementation.

Use the available search tools to gather reliable evidence.

Do not invent facts.

If reliable information cannot be found, say that the information
is unavailable.

After researching, summarize the findings clearly.
"""


market_agent = create_agent(
    model=llm,
    tools=[
        search_market_size,
        search_competitors,
        search_recent_news,
    ],
    system_prompt=SYSTEM_PROMPT,
    response_format=MarketResult,
    name="market_agent",
)