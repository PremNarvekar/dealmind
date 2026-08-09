import os

from dotenv import load_dotenv
from langchain_tavily import TavilySearch


load_dotenv()


tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic",
)


def search_market_size(company_name: str):
    query = (
        f"{company_name} market size TAM SAM SOM"
        f"market size industry revenue growth"
    )

    return tavily_search.invoke({
        "query": query
    })


def search_competitors(company_name: str):
    query = (
        f"{company_name} competitors "
        f"main competitors competing companies alternatives"
    )

    return tavily_search.invoke({
        "query": query
    })


def search_recent_news(company_name: str):
    query = f"{company_name} latest news startup funding product"

    return tavily_search.invoke({
        "query": query,
        "topic": "news",
        "time_range": "month",
    })