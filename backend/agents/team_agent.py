"""
TeamAgent — researches founder backgrounds, team experience, and leadership quality.
"""
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from tools.team_tools import (
    search_founder_profile,
    search_founder_history,
    search_team_strengths_concerns,
)
from models.memo import TeamResult


TEAM_SYSTEM_PROMPT = """
You are the Team Research Agent in an AI investment analysis system.

Your job is to evaluate the startup's founders and leadership team.

Research and analyze:
- Founder backgrounds and professional history
- Previous companies founded or worked at (especially other startups)
- Relevant domain expertise
- Team strengths and notable achievements
- Potential concerns or gaps (missing domain expertise, inexperience, etc.)

Use the available search tools. Do not invent information.

YOUR FINAL OUTPUT MUST BE A RAW JSON OBJECT with the following schema:
{
  "founders": ["string", "string"],
  "previous_companies": ["string", "string"],
  "strengths": ["string", "string"],
  "concerns": ["string", "string"],
  "summary": "string"
}
Ensure the output is ONLY the JSON object, with no markdown formatting or extra text.
"""

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0, max_retries=6)

team_agent = create_agent(
    model=llm,
    tools=[
        search_founder_profile,
        search_founder_history,
        search_team_strengths_concerns,
    ],
    system_prompt=TEAM_SYSTEM_PROMPT,
    name="team_agent",
)