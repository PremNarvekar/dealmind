import os 

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()


tavily_search = TavilySearch(
    max_result=5,
    topic="general",
    search_depth="basic"
)

def search_product_name(company_name: str):
    query= (
        f"{company_name}Products reviews customer feedback"   
    )
    return tavily_search.invoke({
        "query":query
    })
    
def search_tech_stack(company_name: str):
    query= (
        f"{company_name} tech stack technology"
    )
    
    return tavily_search.invoke({
        "query":query
    })
    
    
def search_products_strengths_concerns(company_name: str):
    query = (
        f"{company_name} products strengths weakness"
    )
    
    return tavily_search.invoke({
        "query":query
    })