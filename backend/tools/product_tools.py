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
def search_product_name(company_name: str):
    """Search for the company's product, reviews, customer feedback, and product experience."""

    query = f"{company_name} products reviews customer feedback"

    return tavily_search.invoke({
        "query": query
    })


@tool
def search_tech_stack(company_name: str):
    """Search for the company's technology stack, architecture, and technical implementation."""

    query = f"{company_name} tech stack technology"

    return tavily_search.invoke({
        "query": query
    })


@tool
def search_products_strengths_concerns(company_name: str):
    """Search for product strengths, weaknesses, complaints, and concerns."""

    query = f"{company_name} products strengths weakness"

    return tavily_search.invoke({
        "query": query
    })
