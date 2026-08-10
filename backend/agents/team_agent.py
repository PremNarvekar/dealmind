from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.team_tools import (
    search_founder_profile,
    search_founder_history,
    search_team_strengths_concerns,
)

from models.memo import TeamResult


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
)


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


team_agent = create_agent(
    model=llm,
    tools=[
        search_founder_profile,
        search_founder_history,
        search_team_strengths_concerns,
    ],
    system_prompt=TEAM_SYSTEM_PROMPT,
    response_format=TeamResult,
    name="team_agent",
)