from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langgraph_supervisor import create_supervisor

from .market_agent import market_agent
from .team_agent import team_agent
from .product_agent import product_agent


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
)





SUPERVISOR_PROMPT = """
You are the supervisor of a startup investment research system.

Your job is to coordinate specialist research.

Available specialists:

- run_market_research:
  market size, competitors, industry trends, and recent news.

- run_team_research:
  founder backgrounds, previous companies, experience,
  strengths, and concerns.

- run_product_research:
  product, technology, user feedback, strengths,
  weaknesses, and differentiators.

Rules:

1. Delegate research to the appropriate specialist.
2. Do not perform the research yourself.
3. Do not invent information.
4. Use all relevant specialists when the request requires
   market, team, and product analysis.
5. Collect the research results.
6. Do not make the final investment rating yet.
"""


# Supervisor workflow
workflow = create_supervisor(
    [
        market_agent,
        team_agent,
        product_agent,
    ],
    model=llm,
    prompt=SUPERVISOR_PROMPT,
)


app = workflow.compile()


# if __name__ == "__main__":

#     result = app.invoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "Research Stripe as an investment opportunity."
#                 }
#             ]
#         }
#     )

#     print(result)