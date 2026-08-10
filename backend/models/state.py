from typing import Optional, Annotated

from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from .memo import (
    MarketResult,
    TeamResult,
    ProductResult,
    InvestmentMemo,
)


class GraphState(BaseModel):

    # User input
    company_name: str

    # Agent communication
    messages: Annotated[list[AnyMessage], add_messages] = []

    # Agent results
    market: Optional[MarketResult] = None
    team: Optional[TeamResult] = None
    product: Optional[ProductResult] = None

    # Final output
    investment_memo: Optional[InvestmentMemo] = None

    # Human approval
    approved: bool = False
    auto_approve: bool = False

    # Persistent memory
    thread_id: str

    # Workflow status
    status: str = "pending"

    # Error handling
    error: Optional[str] = None