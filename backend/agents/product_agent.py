from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.product_tools import (
    search_product_name,
    search_tech_stack,
    search_products_strengths_concerns,
)

from models.memo import ProductResult


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
)


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


product_agent = create_agent(
    model=llm,
    tools=[
        search_product_name,
        search_tech_stack,
        search_products_strengths_concerns,
    ],
    system_prompt=PRODUCT_SYSTEM_PROMPT,
    response_format=ProductResult,
    name="product_agent",
)