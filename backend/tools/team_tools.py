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
def search_founder_profile(company_name: str):
    """Search for the founders' backgrounds and professional profiles."""

    query = f"{company_name} founder background"

    return tavily_search.invoke({
        "query": query
    })


@tool
def search_founder_history(company_name: str):
    """Search for founders' previous companies and entrepreneurial experience."""

    query = f"{company_name} founder previous companies"

    return tavily_search.invoke({
        "query": query
    })


@tool
def search_team_strengths_concerns(company_name: str):
    """Search for team strengths, weaknesses, concerns, and leadership issues."""

    query = f"{company_name} team strengths weakness"

    return tavily_search.invoke({
        "query": query
    })
