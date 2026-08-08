import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path


LOG_FILE = Path(__file__).parent / "agent_logs.json"


class AgentLogger(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        fields = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "thread_id": getattr(
                record,
                "thread_id",
                str(threading.get_ident()),
            ),
            "node_name": getattr(record, "node_name", ""),
            "event_type": getattr(record, "event_type", ""),
            "tool_name": getattr(record, "tool_name", ""),
            "token_input": getattr(record, "token_input", 0),
            "token_output": getattr(record, "token_output", 0),
            "cost_usd": getattr(record, "cost_usd", 0.0),
            "latency_ms": getattr(record, "latency_ms", 0),
            "success": getattr(record, "success", True),
            "error": getattr(record, "error", ""),
        }

        return json.dumps(fields)


def get_logger() -> logging.Logger:
    logger = logging.getLogger("dealmind")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    handler.setFormatter(AgentLogger())

    logger.addHandler(handler)

    return logger