import os 

from dotenv import load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


from tools.team_tools import(
    search_founder_profile
    search_founder_history
    search_team_strengths_concerns
    
)

from models.memo import TeamResult 


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0
)

tools = [
    search_founder_profile()
    search_founder_history()
    search_team_strengths_concerns()
]

llm_with_tools = llm.bind_tools(tools)

TEAM_SYSTEM_PROMPT = """
You are the Team Research Agent in an AI investment analysis system.

Your job is to evaluate the startup's founders and team.

Research and analyze:
- Founder backgrounds
- Previous companies and entrepreneurial experience
- Relevant industry experience
- Team strengths
- Potential team weaknesses or concerns

Use the available search tools to gather reliable evidence.

Do not research:
- Market size
- Competitors
- Product technology
- Investment rating

Do not invent or assume information.
Clearly distinguish verified facts from reasonable observations.
If reliable information cannot be found, state that the information is unavailable.

After completing the research, synthesize the evidence into a concise TeamResult.
Focus on information that would actually matter to an investor evaluating the team.
"""


def team_agent(company_name: str) -> TeamResult:
    messages = [
        SystemMessage(content:TEAM_SYSTEM_PROMPT),
        HumanMessage(
            content=f"Research the Team for {company_name}"
        )
    ]
    
    response = llm_with_tools.invoke(message)
    messages.append(response)
    
    while response.tool_calls:
        for tool_calls in response.tool_calls:
            
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            if tool_name == 'search_founder_profile':
                result = search_founder_profile(**tool_args)
                
            elif tool_name == 'search_founder_history':
                result = search_founder_history(**tool_args)
                
            elif tool_name == 'search_team_strengths_concerns':
                result = search_team_strengths_concerns(**tool_args)
                
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
        
    structured_llm = llm.with_structured_output(TeamResult)
    
    final_response = structured_llm.invoke(
        messages
    )
    
    return final_response




