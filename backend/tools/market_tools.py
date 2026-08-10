from dotenv import load_dotenv
from langchain.tools import tool
from langchain_tavily import TavilySearch

load_dotenv()

tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic",
)


@tool
def search_market_size(company_name: str):
    """Search for the company's market size, TAM, SAM, SOM, industry revenue, and growth."""

    query = (
        f"{company_name} market size TAM SAM SOM "
        f"market size industry revenue growth"
    )

    return tavily_search.invoke({
        "query": query
    })


@tool
def search_competitors(company_name: str):
    """Search for the company's main competitors and competing alternatives."""

    query = (
        f"{company_name} competitors "
        f"main competitors competing companies alternatives"
    )

    return tavily_search.invoke({
        "query": query
    })


@tool
def search_recent_news(company_name: str):
    """Search for recent relevant news, funding, products, and company developments."""

    query = f"{company_name} latest news startup funding product"

    return tavily_search.invoke({
        "query": query,
        "topic": "news",
        "time_range": "month",
    })