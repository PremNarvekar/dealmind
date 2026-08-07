from pydantic import BaseModel
from typing import Optional

from .memo import (
    MarketResult,
    TeamResult,
    ProductResult,
    InvestmentMemo,
)


class GraphState(BaseModel):
    
    # User Input
    
    company_name: str


    # Agent Results

    market: Optional[MarketResult] = None
    team: Optional[TeamResult] = None
    product: Optional[ProductResult] = None


    # Final Output
    investment_memo: Optional[InvestmentMemo] = None

    
    # Human In The Loop
    approved: bool = False
    auto_approve: bool = False

    
    # Persistent Memory
    thread_id: str


    # Workflow Status
    status: str = "pending"


    # Error Handling
    error: Optional[str] = None