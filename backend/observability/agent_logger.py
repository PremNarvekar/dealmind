"""
Agent Logger — structured JSON observability for the DealMind workflow.

Design decisions:
- Uses python-json-logger for machine-parseable structured logs.
- Logs go to stdout (12-factor app standard) so the container runtime can
  forward them to any log aggregation system (CloudWatch, Datadog, etc.).
- A rotating file handler also writes to agent_logs.json for local dev.
- NEVER logs secrets, API keys, or database credentials.
- Each log record includes: timestamp, level, event, run_id, company_name,
  agent, latency_ms, success, error_type.
"""
import logging
import logging.handlers
import os
import time
from typing import Optional

from pythonjsonlogger.json import JsonFormatter


# ── Logger setup ─────────────────────────────────────────────────────────────

logger = logging.getLogger("dealmind")
logger.setLevel(logging.INFO)
logger.propagate = False  # don't double-log to the root logger

if not logger.handlers:
    # Stdout handler — always present
    _stdout_handler = logging.StreamHandler()
    _stdout_handler.setFormatter(JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.addHandler(_stdout_handler)

    # File handler — local development convenience
    _log_dir = os.path.dirname(__file__)
    _log_file = os.path.join(_log_dir, "agent_logs.json")
    try:
        _file_handler = logging.handlers.RotatingFileHandler(
            _log_file, maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        _file_handler.setFormatter(JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(_file_handler)
    except (OSError, PermissionError):
        # If we can't write to disk (e.g. read-only container), log only to stdout.
        pass


# ── Public logging helpers ────────────────────────────────────────────────────

def log_run_start(run_id: str, company_name: str) -> None:
    logger.info(
        "run_started",
        extra={"run_id": run_id, "company_name": company_name, "event": "run_started"},
    )


def log_run_complete(run_id: str, company_name: str, latency_ms: float) -> None:
    logger.info(
        "run_completed",
        extra={
            "run_id": run_id,
            "company_name": company_name,
            "event": "run_completed",
            "latency_ms": round(latency_ms, 2),
        },
    )


def log_run_error(run_id: str, company_name: Optional[str], error: Exception) -> None:
    logger.exception(
        "run_failed",
        extra={
            "run_id": run_id,
            "company_name": company_name,
            "event": "run_failed",
            "error_type": type(error).__name__,
        },
    )


def log_agent_start(run_id: str, agent_name: str, company_name: str) -> None:
    logger.info(
        "agent_started",
        extra={
            "run_id": run_id,
            "agent": agent_name,
            "company_name": company_name,
            "event": "agent_started",
        },
    )


def log_agent_complete(
    run_id: str,
    agent_name: str,
    company_name: str,
    latency_ms: float,
    success: bool,
    error_type: Optional[str] = None,
) -> None:
    logger.info(
        "agent_completed",
        extra={
            "run_id": run_id,
            "agent": agent_name,
            "company_name": company_name,
            "event": "agent_completed",
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "error_type": error_type,
        },
    )


def log_node_start(run_id: str, node_name: str, company_name: str) -> None:
    logger.info(
        "node_started",
        extra={
            "run_id": run_id,
            "node": node_name,
            "company_name": company_name,
            "event": "node_started",
        },
    )


def log_node_complete(
    run_id: str,
    node_name: str,
    company_name: str,
    latency_ms: float,
    success: bool,
    error_type: Optional[str] = None,
) -> None:
    logger.info(
        "node_completed",
        extra={
            "run_id": run_id,
            "node": node_name,
            "company_name": company_name,
            "event": "node_completed",
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "error_type": error_type,
        },
    )


# ── Convenience timer context ────────────────────────────────────────────────

class timer:
    """Simple wall-clock timer for measuring node latency."""

    def __init__(self) -> None:
        self._start = time.monotonic()

    def elapsed_ms(self) -> float:
        return (time.monotonic() - self._start) * 1000