from agents.market_agent import market_agent
from agents.team_agent import team_agent
from agents.product_agent import product_agent


company = "Stripe"


print("\n========== MARKET AGENT ==========")
market_result = market_agent(company)
print(market_result)


print("\n========== TEAM AGENT ==========")
team_result = team_agent(company)
print(team_result)


print("\n========== PRODUCT AGENT ==========")
product_result = product_agent(company)
print(product_result)