import os 

from dotenv import load_dotenv
from langchain_tavily import TavilySearch


load_dotenv()

tavily_search = TavilySearch(
    max_result= 5,
    topic="general",
    search_depth="basic"
    
)

def search_founder_profile(company_name: str):
    query = (
        f"{company_name} founder background"
    
    )
    return tavily_search.invoke({
        "query":query
    })
    
def search_founder_history(company_name: str):
    query = (
        f"{company_name} founder previous companies"
    
    )
    return tavily_search.invoke({
        "query": query
    })
    
    
def search_team_strengths_concerns(company_name: str):
    query = (
        f"{company_name} team strengths weakness"
    )
    return tavily_search.invoke({
        "query":query
    })