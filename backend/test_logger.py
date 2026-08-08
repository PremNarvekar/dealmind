from logging.agent_logger import get_logger


logger = get_logger()


logger.info(
    "Market search completed",
    extra={
        "thread_id": "test-123",
        "node_name": "market_agent",
        "event_type": "tool_call",
        "tool_name": "tavily_search",
        "token_input": 0,
        "token_output": 0,
        "cost_usd": 0.0,
        "latency_ms": 820,
        "success": True,
        "error": "",
    },
)