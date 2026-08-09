import os 

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage , SystemMessage, ToolMessage
from tools.product_tools import (
    search_product_name,
    search_tech_stack,
    search_products_strengths_concerns
)

from models.memo import ProductResult


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0
)

tools = [
    search_product_name,
    search_tech_stack,
    search_products_strengths_concerns

]

llm_with_tools = llm.bind_tools(tools)

PRODUCT_SYSTEM_PROMPT = """
You are the Product Research Agent in an AI investment analysis system.

Your job is to evaluate the startup's product.

Research and analyze:
- Product quality and user feedback
- Product strengths and weaknesses
- Customer complaints
- Technology and tech stack
- Technical differentiators
- AI/ML capabilities and integrations

Use the available search tools to gather reliable evidence.

Do not research:
- Market size
- Competitors
- Founder backgrounds
- Investment rating

Do not invent or assume information.
Clearly distinguish verified facts from reasonable observations.
If reliable information cannot be found, state that the information is unavailable.

After completing the research, synthesize the evidence into a concise ProductResult.
Focus on information that would actually matter to an investor evaluating the product.
"""

def product_agent(company_name:str) -> ProductResult:
    messages = [
        SystemMessage(content=PRODUCT_SYSTEM_PROMPT),
        HumanMessage(
            content=f"Search products of {company_name}."
        )
    ]
    
    response = llm_with_tools.invoke(messages)
    messages.append(response)
    
    while response.tool_calls:
        
        for tool_call in response.tool_calls:
            
            name = tool_call['name']
            args = tool_call['args']
            
            if name == 'search_product_name':
                result = search_product_name(**args)
                
            elif name == "search_tech_stack":
                result = search_tech_stack(**args)
                
            elif name == "search_products_strengths_concerns":
                result = search_products_strengths_concerns(**args)
            
            else:
                continue 
            
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
                
                
            )
            
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        
    structured_llm = llm.with_structured_output(ProductResult)
    final_response = structured_llm.invoke(
        messages
    )
    
    return final_response