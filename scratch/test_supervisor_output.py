import sys
sys.path.insert(0, 'backend')
from dotenv import load_dotenv
load_dotenv('backend/.env')
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor
from pydantic import BaseModel, Field
import json

class SimpleResult(BaseModel):
    summary: str = Field(description='summary')

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0)

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt='Say hello and return a SimpleResult with a summary.',
    response_format=SimpleResult,
    name='my_agent'
)
super_wf = create_supervisor(agents=[agent], model=llm, prompt='Call my_agent and stop.', output_mode='last_message')
app = super_wf.compile()

res = app.invoke({'messages': [('user', 'do it')]})
print('SUPERVISOR RAW OUTPUT:')
for m in res['messages']:
    print(f'[{m.name or m.type}] {m.__class__.__name__}: content={m.content!r}')
    if hasattr(m, 'tool_calls'):
        print(f'  tool_calls: {m.tool_calls}')
    if hasattr(m, 'additional_kwargs'):
        print(f'  additional_kwargs: {m.additional_kwargs}')
