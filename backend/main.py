"""
DealMind FastAPI Application Entry Point.

Startup sequence (via lifespan context manager):
1. Validate config (happens at import of config.py — fails fast if .env missing).
2. Setup PostgreSQL checkpointer (runs schema migrations exactly once).
3. Build and compile the LangGraph graph (with the checkpointer attached).
4. Register the graph instance with the API router.

Shutdown sequence:
5. Close the PostgreSQL connection pool.

This ordering is critical:
  - Checkpointer must be set up before graph.compile() is called.
  - Graph must be built before any request can be handled.
  - Secrets (DATABASE_URL password) never appear in logs.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config  # noqa: F401 — triggers validation of all required env vars
from graph.checkpoint import setup_checkpointer, shutdown_checkpointer
from graph.graph import build_graph
import graph.graph as graph_module
from api.routes import router, set_graph

logger = logging.getLogger("dealmind.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("dealmind.starting")

    logger.info("dealmind.checkpoint_setup")
    setup_checkpointer()

    logger.info("dealmind.graph_build")
    compiled_graph = build_graph()
    graph_module.app = compiled_graph  # make it available to any module that imports it
    set_graph(compiled_graph)          # inject into the API router

    # Start the background worker for decoupling
    import asyncio
    from api.routes import research_worker
    worker_task = asyncio.create_task(research_worker())

    logger.info("dealmind.ready")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("dealmind.shutdown")
    worker_task.cancel()
    shutdown_checkpointer()


app = FastAPI(
    title="DealMind — Startup Investment Research API",
    version="1.0.0",
    description=(
        "AI-powered multi-agent system for investment research. "
        "Researches market, team, and product for any startup, "
        "then synthesizes a structured InvestmentMemo."
    ),
    lifespan=lifespan,
)

# Allow CORS for frontend (production + local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["Infrastructure"])
def health_check():
    """
    Health check endpoint for load balancers and container orchestrators.
    Returns 200 if the application is running and the graph is initialized.
    """
    graph_ready = graph_module.app is not None
    return {
        "status": "ok" if graph_ready else "starting",
        "graph_ready": graph_ready,
    }