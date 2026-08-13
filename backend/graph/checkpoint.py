"""
In-memory checkpointing for LangGraph.

Switched to MemorySaver for local testing without needing a real Postgres database.
"""
from __future__ import annotations

import logging
from typing import Optional

from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger("dealmind.checkpoint")

# ── Module-level singletons ───
_checkpointer: Optional[MemorySaver] = None

def get_checkpointer() -> MemorySaver:
    global _checkpointer

    if _checkpointer is not None:
        return _checkpointer

    logger.info("checkpoint.memory_init")
    _checkpointer = MemorySaver()
    return _checkpointer


def setup_checkpointer() -> MemorySaver:
    """
    Setup MemorySaver.
    """
    checkpointer = get_checkpointer()
    logger.info("checkpoint.setup_complete")
    return checkpointer


def shutdown_checkpointer() -> None:
    """
    Shutdown MemorySaver.
    """
    global _checkpointer
    _checkpointer = None
    logger.info("checkpoint.shutdown_complete")