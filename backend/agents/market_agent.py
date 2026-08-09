import os 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from tools.market_tools import (
    
    search_market_size,
    search_competitors,
    search_recent_news,
)

from models.memo import MarketResult


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0
)

tools = [
    search_market_size,
    search_competitors,
    search_recent_news,
]

llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT ="""
You are the Market Research Agent for an investment analysis system.

Your responsibility is ONLY to research:
- market size
- competitors
- recent relevant news
- industry growth and trends

Do not research founders, team backgrounds, or technical implementation.

Use the available search tools to gather evidence.

Do not invent facts. If reliable information cannot be found,
say that the information is unavailable.

After researching, summarize the findings clearly.

"""
def market_agent(company_name: str) -> MarketResult:
    message = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"Research the market for {company_name}."
            
        )
        
    ]
    response = llm_with_tools.invoke(message)
    message.append(response)
    
    while response.tool_Calls:
        
        for tool_call in response.tool_calls:
            
        
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
        
            if tool_name == "search_market_size":
                result = search_market_size(**tool_args)
            
            elif tool_name == "search_competitors":
                result = search_competitors(**tool_args)
            
            elif tool_name == "search_recent_news":
                result = search_recent_news(**tool_args)
            
            else:
                continue 
        
            message.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                
            )
        )
            
        response = llm_with_tools.invoke(messages)
        message.append(response)
        
    structured_llm = llm.with_structured_output(MarketResult)
    
    final_response = structured_llm.invoke(
        message
    )
    
    return final_response

    
