"""
Research API Routes.

POST /api/research
  - Validates input
  - Generates a unique research_run_id (UUID)
  - Invokes the LangGraph graph
  - Returns a structured response containing the InvestmentMemo

Design decisions:
- UUID per request ensures different requests for the same company
  have independent checkpoint threads and don't overwrite each other.
- The graph is injected via set_graph() during FastAPI lifespan startup
  to avoid circular imports and module-level side effects.
- Errors are caught and returned as structured 500 responses (not raw
  LangGraph exceptions or tracebacks).
- The response is a clean Pydantic model — not raw LangGraph message state.
"""
from __future__ import annotations

import uuid
import time
import logging
import json
import asyncio
from typing import Optional, Any, AsyncGenerator

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from models.memo import InvestmentMemo
from observability.agent_logger import log_run_start, log_run_complete, log_run_error
from api.cache import get_cached_memo, set_cached_memo

logger = logging.getLogger("dealmind.api")

# ── Pydantic request / response models ───────────────────────────────────────

class ResearchRequest(BaseModel):
    company_name: str
    selected_agents: list[str] = ["market", "team", "product"]

    @field_validator("company_name")
    @classmethod
    def company_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("company_name must not be empty")
        if len(v) > 200:
            raise ValueError("company_name must be 200 characters or fewer")
        return v


class ResearchResponse(BaseModel):
    research_run_id: str
    company_name: str
    status: str
    investment_memo: Optional[InvestmentMemo] = None
    error: Optional[str] = None


# ── Router setup ──────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api", tags=["Research"])

# The compiled graph is injected here by main.py lifespan.
_graph: Any = None

# --- DECOUPLING INFRASTRUCTURE (Simulating Celery + Redis PubSub) ---
# job_queue stores pending research jobs
job_queue: asyncio.Queue = asyncio.Queue()
# active_streams maps a run_id to a queue of SSE events
active_streams: dict[str, asyncio.Queue] = {}

def set_graph(graph) -> None:
    """Called by main.py lifespan after the graph is built."""
    global _graph
    _graph = graph

async def research_worker():
    """
    Background worker simulating a Celery process.
    Consumes jobs from the job_queue, executes LangGraph, and publishes events.
    """
    logger.info("dealmind.worker.started")
    while True:
        try:
            job = await job_queue.get()
            if job is None:
                break # Shutdown signal
                
            run_id, company_name, graph_input, graph_config = job
            stream_queue = active_streams.get(run_id)
            if not stream_queue:
                continue

            start_ms = time.monotonic() * 1000
            
            try:
                async for output in _graph.astream(graph_input, config=graph_config, stream_mode="updates"):
                    for node_name, state_update in output.items():
                        await stream_queue.put(f"data: {json.dumps({'type': 'node_update', 'node': node_name})}\n\n")
                        await asyncio.sleep(0.05)
                
                final_state = await _graph.aget_state(graph_config)
                elapsed_ms = time.monotonic() * 1000 - start_ms
                log_run_complete(run_id, company_name, elapsed_ms)

                state_values = final_state.values
                investment_memo = state_values.get("investment_memo")
                memo_dict = investment_memo.model_dump() if investment_memo else None
                
                # Update Cache
                if investment_memo:
                    set_cached_memo(company_name, investment_memo)

                result_payload = {
                    "type": "complete",
                    "result": {
                        "research_run_id": run_id,
                        "company_name": company_name,
                        "status": state_values.get("status", "unknown"),
                        "investment_memo": memo_dict,
                        "error": state_values.get("error"),
                    }
                }
                await stream_queue.put(f"data: {json.dumps(result_payload)}\n\n")
            except Exception as e:
                log_run_error(run_id, company_name, e)
                logger.exception("worker_graph_failed", extra={"run_id": run_id})
                await stream_queue.put(f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n")
            finally:
                await stream_queue.put(None) # EOF marker
                
        except Exception as e:
            logger.exception("worker_loop_error")


# ── Route handlers ────────────────────────────────────────────────────────────

@router.post("/research")
async def research_company(request: ResearchRequest) -> StreamingResponse:
    """
    Research a startup for investment using SSE (Server-Sent Events).
    
    Streams progress events to the client in real-time.
    Uses Caching and Decoupled Background Workers.
    """
    if _graph is None:
        raise HTTPException(
            status_code=503,
            detail="Graph not yet initialized. Server may still be starting up.",
        )

    company_name = request.company_name
    
    # 1. Check Cache
    cached_memo = get_cached_memo(company_name)
    if cached_memo:
        async def cached_event_generator():
            yield f"data: {json.dumps({'type': 'start', 'run_id': 'cached-run'})}\n\n"
            await asyncio.sleep(0.1) # Simulate brief network latency
            result_payload = {
                "type": "complete",
                "result": {
                    "research_run_id": "cached-run",
                    "company_name": company_name,
                    "status": "complete",
                    "investment_memo": cached_memo.model_dump(),
                    "error": None,
                }
            }
            yield f"data: {json.dumps(result_payload)}\n\n"
        return StreamingResponse(cached_event_generator(), media_type="text/event-stream")

    # 2. Dispatch to decoupled worker queue
    research_run_id = str(uuid.uuid4())
    log_run_start(research_run_id, company_name)

    graph_input = {
        "company_name": company_name,
        "thread_id": research_run_id,
        "selected_agents": request.selected_agents,
        "messages": [],
        "market": None,
        "team": None,
        "product": None,
        "investment_memo": None,
        "approved": False,
        "auto_approve": True,
        "status": "pending",
        "error": None,
    }

    graph_config = {
        "configurable": {"thread_id": research_run_id}
    }

    # Setup PubSub stream queue
    stream_queue = asyncio.Queue()
    active_streams[research_run_id] = stream_queue

    # Push to Job Queue
    await job_queue.put((research_run_id, company_name, graph_input, graph_config))

    async def event_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'type': 'start', 'run_id': research_run_id})}\n\n"
        try:
            while True:
                # Poll PubSub queue (prevents blocking FastAPI thread)
                event = await stream_queue.get()
                if event is None:
                    break # EOF
                yield event
        finally:
            # Cleanup
            active_streams.pop(research_run_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/research/{run_id}/approve")
async def approve_research(run_id: str) -> StreamingResponse:
    if _graph is None:
        raise HTTPException(status_code=503, detail="Graph not initialized")

    graph_config = {"configurable": {"thread_id": run_id}}
    state = await _graph.aget_state(graph_config)
    
    if not state.next:
        raise HTTPException(status_code=400, detail="Run is not pending approval")

    async def event_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'type': 'resume', 'run_id': run_id})}\n\n"
        try:
            async for output in _graph.astream(None, config=graph_config, stream_mode="updates"):
                for node_name, state_update in output.items():
                    yield f"data: {json.dumps({'type': 'node_update', 'node': node_name})}\n\n"
                    await asyncio.sleep(0.05)
            
            final_state = await _graph.aget_state(graph_config)
            state_values = final_state.values
            investment_memo = state_values.get("investment_memo")
            memo_dict = investment_memo.model_dump() if investment_memo else None
            
            result_payload = {
                "type": "complete",
                "result": {
                    "research_run_id": run_id,
                    "company_name": state_values.get("company_name", ""),
                    "status": state_values.get("status", "unknown"),
                    "investment_memo": memo_dict,
                    "error": state_values.get("error"),
                }
            }
            yield f"data: {json.dumps(result_payload)}\n\n"
        except Exception as e:
            logger.exception("approve_stream_failed")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")