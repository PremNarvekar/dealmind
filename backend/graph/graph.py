"""
Graph — the top-level LangGraph orchestration for DealMind.

Architecture:
  START
    ↓
  [supervisor_node]       — runs the compiled supervisor subgraph which
                            dispatches market_agent, team_agent, product_agent
    ↓
  [extract_results_node]  — extracts structured_response from each agent's
                            last message and stores in GraphState
    ↓
  [validate_research_node]— checks we have enough data to synthesize
    ↓
  [synthesize_memo_node]  — calls LLM with structured output to produce
                            the final InvestmentMemo
    ↓
  END

State flow:
  GraphState.messages accumulates all messages (via add_messages reducer).
  GraphState.market / .team / .product are populated by extract_results_node.
  GraphState.investment_memo is populated by synthesize_memo_node.
  GraphState.status tracks workflow phase.

Checkpointing:
  The outer graph is compiled with the PostgresSaver checkpointer.
  Every state transition is saved to PostgreSQL automatically by LangGraph.

Design decision — why a separate outer graph instead of just the supervisor?
  The supervisor subgraph uses MessagesState internally and returns messages.
  Our outer graph needs additional typed state fields (market, team, product,
  investment_memo). These cannot live inside the supervisor's MessagesState.
  The outer graph owns GraphState. The supervisor is one node within it.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from langchain_core.messages import AIMessage, AnyMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from config import GEMINI_MODEL
from models.state import GraphState
from models.memo import MarketResult, TeamResult, ProductResult, InvestmentMemo
from agents.supervisor import supervisor_workflow
from graph.checkpoint import get_checkpointer
from observability.agent_logger import (
    log_node_start,
    log_node_complete,
    timer,
)

logger = logging.getLogger("dealmind.graph")


# ── Synthesis LLM (separate instance, can use a more capable model) ──────────
_synthesis_llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0, max_retries=6)
_synthesis_llm_structured = _synthesis_llm.with_structured_output(InvestmentMemo)

SYNTHESIS_PROMPT = """
You are a senior investment analyst. You have been given the following
research reports for {company_name}.

MARKET RESEARCH:
{market_json}

TEAM RESEARCH:
{team_json}

PRODUCT RESEARCH:
{product_json}

Based ONLY on the information provided above, produce a structured
InvestmentMemo. Do not invent facts not present in the research.

When information was unavailable or unreliable:
- Note it in the missing_information field.
- Do not assume it is positive.

Produce a fair, evidence-based assessment. Rate on a scale of 1–10.
"""


# ── Helper: extract structured_response from supervisor output messages ───────

def _extract_agent_result(messages: list[AnyMessage], agent_name: str) -> Any | None:
    """
    Walk messages in reverse to find the last AIMessage from the named agent
    that has a structured_response attached.

    The langgraph-supervisor package attaches the agent's CompiledStateGraph
    output as additional_kwargs["structured_response"] on the forwarded message,
    OR the agent node itself may include it in message.content as a JSON blob.

    We try multiple extraction strategies:
    1. message.additional_kwargs["structured_response"]
    2. Parse message.content as JSON if it looks like a dict
    3. Return None and let the validation node catch it.
    """
    logger.info(f"Extracting for {agent_name}. Total messages: {len(messages)}")
    for msg in messages:
        logger.info(f"MSG: type={type(msg)}, name={getattr(msg, 'name', None)}, content={msg.content[:50]}..., kwargs={getattr(msg, 'additional_kwargs', {})}")

    for msg in reversed(messages):
        if not isinstance(msg, AIMessage):
            continue
        
        # Check name if available
        if getattr(msg, "name", None) != agent_name:
            continue

        # Strategy 1: additional_kwargs
        sr = msg.additional_kwargs.get("structured_response")
        if sr is not None:
            return sr

        # Strategy 2: content is a JSON object
        content = msg.content
        if isinstance(content, str):
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            if content.startswith("{"):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass

        # Strategy 3: content is already a dict (some integrations return this)
        if isinstance(content, dict):
            return content

    return None


# ── Node 1: supervisor_node ───────────────────────────────────────────────────

# Compile the supervisor workflow. We do NOT attach a checkpointer here —
# the outer graph checkpointer handles everything.
_compiled_supervisor = supervisor_workflow.compile()


def supervisor_node(state: GraphState) -> dict:
    """
    Invoke the compiled supervisor subgraph.

    The supervisor internally handles routing to market_agent, team_agent,
    and product_agent. It returns a final messages list.

    We pass the company_name in the initial user message so the agents
    know what to research.
    """
    run_id = state["thread_id"]
    company_name = state["company_name"]
    t = timer()
    log_node_start(run_id, "supervisor", company_name)

    try:
        selected_agents = state.get("selected_agents", ["market", "team", "product"])
        agent_names = [f"{agent}_agent" for agent in selected_agents]
        agents_str = ", ".join(agent_names)

        supervisor_input = {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Research {company_name} as an investment opportunity. "
                        f"Call {agents_str} to gather comprehensive research."
                    ),
                }
            ]
        }

        result = _compiled_supervisor.invoke(supervisor_input)

        log_node_complete(run_id, "supervisor", company_name, t.elapsed_ms(), success=True)
        return {
            "messages": result.get("messages", []),
            "status": "researching",
        }

    except Exception as e:
        log_node_complete(run_id, "supervisor", company_name, t.elapsed_ms(), success=False, error_type=type(e).__name__)
        logger.exception("supervisor_node_failed", extra={"run_id": run_id, "company_name": company_name})
        return {"status": "error", "error": f"Supervisor failed: {type(e).__name__}: {e}"}


# ── Node 2: extract_results_node ──────────────────────────────────────────────

def extract_results_node(state: GraphState) -> dict:
    """
    After the supervisor completes, extract structured research results from
    the message history and store them in typed GraphState fields.

    The create_agent() function produces agents whose structured_response
    (the Pydantic output) is embedded in agent messages. We locate those
    messages and parse the results.

    If extraction fails for an agent, we log a warning and set that field
    to a placeholder so synthesis can flag missing data.
    """
    run_id = state["thread_id"]
    company_name = state["company_name"]
    messages = state.get("messages", [])
    t = timer()
    log_node_start(run_id, "extract_results", company_name)

    updates: dict = {}

    # Market result
    raw_market = _extract_agent_result(messages, "market_agent")
    if raw_market:
        try:
            updates["market"] = (
                MarketResult(**raw_market) if isinstance(raw_market, dict) else raw_market
            )
        except Exception as e:
            logger.warning("market_result_parse_failed", extra={"run_id": run_id, "error": str(e)})
            updates["market"] = MarketResult(
                market_size="Data unavailable",
                summary=f"Market research extraction failed: {e}",
            )
    else:
        logger.warning("market_result_not_found", extra={"run_id": run_id})
        updates["market"] = MarketResult(
            market_size="Data unavailable",
            summary="Market research was not captured in messages.",
        )

    # Team result
    raw_team = _extract_agent_result(messages, "team_agent")
    if raw_team:
        try:
            updates["team"] = (
                TeamResult(**raw_team) if isinstance(raw_team, dict) else raw_team
            )
        except Exception as e:
            logger.warning("team_result_parse_failed", extra={"run_id": run_id, "error": str(e)})
            updates["team"] = TeamResult(
                summary=f"Team research extraction failed: {e}",
            )
    else:
        logger.warning("team_result_not_found", extra={"run_id": run_id})
        updates["team"] = TeamResult(summary="Team research was not captured in messages.")

    # Product result
    raw_product = _extract_agent_result(messages, "product_agent")
    if raw_product:
        try:
            updates["product"] = (
                ProductResult(**raw_product) if isinstance(raw_product, dict) else raw_product
            )
        except Exception as e:
            logger.warning("product_result_parse_failed", extra={"run_id": run_id, "error": str(e)})
            updates["product"] = ProductResult(
                product_name=company_name,
                summary=f"Product research extraction failed: {e}",
            )
    else:
        logger.warning("product_result_not_found", extra={"run_id": run_id})
        updates["product"] = ProductResult(
            product_name=company_name,
            summary="Product research was not captured in messages.",
        )

    log_node_complete(run_id, "extract_results", company_name, t.elapsed_ms(), success=True)
    return updates


# ── Node 3: validate_research_node ───────────────────────────────────────────

def validate_research_node(state: GraphState) -> dict:
    """
    Light validation before synthesis.

    We always proceed to synthesis — even with incomplete data — because
    the synthesis prompt instructs the LLM to flag missing information in
    the missing_information field rather than inventing facts.

    This node exists as an explicit checkpoint: it logs the data quality
    and could be extended to interrupt for human review if needed.
    """
    run_id = state["thread_id"]
    company_name = state["company_name"]
    t = timer()
    log_node_start(run_id, "validate_research", company_name)

    market_ok = state.get("market") is not None
    team_ok = state.get("team") is not None
    product_ok = state.get("product") is not None

    logger.info(
        "research_validation",
        extra={
            "run_id": run_id,
            "company_name": company_name,
            "market_ok": market_ok,
            "team_ok": team_ok,
            "product_ok": product_ok,
        },
    )

    log_node_complete(run_id, "validate_research", company_name, t.elapsed_ms(), success=True)
    return {"status": "needs_approval"}


# ── Node 4: synthesize_memo_node ──────────────────────────────────────────────

def synthesize_memo_node(state: GraphState) -> dict:
    """
    Takes MarketResult + TeamResult + ProductResult from state and calls
    the LLM with structured output (InvestmentMemo schema) to produce the
    final investment analysis.

    This is the ONLY place where the investment rating and recommendation
    are produced. The supervisor and specialist agents do NOT rate.
    """
    run_id = state["thread_id"]
    company_name = state["company_name"]
    t = timer()
    log_node_start(run_id, "synthesize_memo", company_name)

    try:
        market: MarketResult = state["market"]
        team: TeamResult = state["team"]
        product: ProductResult = state["product"]

        prompt = SYNTHESIS_PROMPT.format(
            company_name=company_name,
            market_json=market.model_dump_json(indent=2),
            team_json=team.model_dump_json(indent=2),
            product_json=product.model_dump_json(indent=2),
        )

        memo: InvestmentMemo = _synthesis_llm_structured.invoke(prompt)

        log_node_complete(run_id, "synthesize_memo", company_name, t.elapsed_ms(), success=True)
        return {"investment_memo": memo, "status": "complete"}

    except Exception as e:
        log_node_complete(
            run_id, "synthesize_memo", company_name, t.elapsed_ms(),
            success=False, error_type=type(e).__name__
        )
        logger.exception("synthesis_failed", extra={"run_id": run_id, "company_name": company_name})
        return {"status": "error", "error": f"Synthesis failed: {type(e).__name__}: {e}"}


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph():
    """
    Build and compile the DealMind research graph.

    Called once during FastAPI lifespan startup AFTER the checkpointer
    has been initialized and setup() has run.
    """
    graph = StateGraph(GraphState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("extract_results", extract_results_node)
    graph.add_node("validate_research", validate_research_node)
    graph.add_node("synthesize_memo", synthesize_memo_node)

    graph.add_edge(START, "supervisor")
    graph.add_edge("supervisor", "extract_results")
    graph.add_edge("extract_results", "validate_research")
    graph.add_edge("validate_research", "synthesize_memo")
    graph.add_edge("synthesize_memo", END)

    checkpointer = get_checkpointer()
    return graph.compile(checkpointer=checkpointer, interrupt_before=["synthesize_memo"])


# Module-level app instance — populated during FastAPI lifespan.
# Do NOT import this at module level before lifespan has run.
app = None  # type: ignore[assignment]