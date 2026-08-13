"""
GraphState — the single source of truth for the DealMind research workflow.

Design decisions:
- TypedDict (not Pydantic BaseModel) because LangGraph uses TypedDict's
  __annotations__ to discover channels and reducers. Pydantic BaseModel
  breaks reducer detection and checkpoint serialization.
- messages uses Annotated[..., add_messages] so LangGraph appends instead
  of replacing messages on every state update.
- All research result fields (market, team, product, investment_memo) are
  Optional so the graph can start with just company_name + messages.
- thread_id is the per-run UUID, stored in state for logging/observability.
"""
from __future__ import annotations

from typing import Annotated, Optional
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from models.memo import MarketResult, TeamResult, ProductResult, InvestmentMemo


class GraphState(TypedDict):
    # ── Inputs ──────────────────────────────────────────────────────────────
    company_name: str
    thread_id: str                     # UUID generated per request
    selected_agents: list[str]         # list of agent names to run (e.g. ['market', 'team', 'product'])

    # ── Agent communication (append-only via add_messages reducer) ──────────
    messages: Annotated[list[AnyMessage], add_messages]

    # ── Specialist research results ──────────────────────────────────────────
    market: Optional[MarketResult]
    team: Optional[TeamResult]
    product: Optional[ProductResult]

    # ── Final output ─────────────────────────────────────────────────────────
    investment_memo: Optional[InvestmentMemo]

    # ── Workflow control ─────────────────────────────────────────────────────
    approved: bool
    auto_approve: bool
    status: str                        # pending | researching | synthesizing | complete | error

    # ── Error tracking ───────────────────────────────────────────────────────
    error: Optional[str]