"""
test_api.py — Tests for FastAPI routes (graph and checkpointer mocked).
"""
import uuid
import json
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

def _parse_sse_complete_event(response_text: str) -> dict:
    """Helper to extract the final 'complete' JSON payload from an SSE response."""
    for line in response_text.split("\n"):
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if data.get("type") == "complete":
                return data.get("result", {})
    return {}

@pytest.fixture
def client_with_mock_graph(sample_investment_memo):
    """
    FastAPI test client with a mocked graph that returns a successful result.
    Bypasses real database, LLM, and Tavily calls entirely.
    """
    from fastapi import FastAPI
    from contextlib import asynccontextmanager
    from api.routes import router, set_graph
    from graph import graph as graph_module
    from dataclasses import dataclass

    mock_graph = MagicMock()
    
    # Mock astream to yield a dummy update
    async def mock_astream(*args, **kwargs):
        yield {"supervisor": {"messages": []}}
    mock_graph.astream = mock_astream

    @dataclass
    class MockState:
        values: dict
        next: tuple = ()

    # Mock aget_state to return our desired final state
    mock_final_state = {
        "company_name": "Stripe",
        "thread_id": str(uuid.uuid4()),
        "messages": [],
        "market": sample_investment_memo.market,
        "team": sample_investment_memo.team,
        "product": sample_investment_memo.product,
        "investment_memo": sample_investment_memo,
        "approved": True,
        "auto_approve": True,
        "status": "complete",
        "error": None,
    }
    mock_graph.aget_state = AsyncMock(return_value=MockState(values=mock_final_state))

    @asynccontextmanager
    async def mock_lifespan(app):
        set_graph(mock_graph)
        graph_module.app = mock_graph
        yield
        set_graph(None)
        graph_module.app = None

    test_app = FastAPI(lifespan=mock_lifespan)
    test_app.test_mock_graph = mock_graph

    @test_app.get("/health")
    def health():
        return {"status": "ok", "graph_ready": True}

    test_app.include_router(router)

    with TestClient(test_app) as c:
        yield c, mock_graph


@pytest.fixture
def client_with_error_graph():
    """Test client whose graph always raises an exception."""
    from fastapi import FastAPI
    from contextlib import asynccontextmanager
    from api.routes import router, set_graph
    from graph import graph as graph_module

    mock_graph = MagicMock()
    
    async def mock_astream_error(*args, **kwargs):
        raise RuntimeError("Simulated graph failure")
        yield {} # Unreachable

    mock_graph.astream = mock_astream_error

    @asynccontextmanager
    async def mock_lifespan(app):
        set_graph(mock_graph)
        graph_module.app = mock_graph
        yield
        set_graph(None)
        graph_module.app = None

    test_app = FastAPI(lifespan=mock_lifespan)
    test_app.include_router(router)

    with TestClient(test_app, raise_server_exceptions=False) as c:
        yield c


class TestHealthCheck:
    def test_health_returns_200(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_body(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        body = client.get("/health").json()
        assert body["status"] == "ok"
        assert body["graph_ready"] is True


class TestResearchEndpoint:
    def test_successful_research_returns_200(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        response = client.post("/api/research", json={"company_name": "Stripe"})
        assert response.status_code == 200

    def test_response_has_correct_structure(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        response = client.post("/api/research", json={"company_name": "Stripe"})
        body = _parse_sse_complete_event(response.text)
        assert "research_run_id" in body
        assert "company_name" in body
        assert "status" in body
        assert "investment_memo" in body

    def test_response_contains_investment_memo(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        response = client.post("/api/research", json={"company_name": "Stripe"})
        body = _parse_sse_complete_event(response.text)
        memo = body["investment_memo"]
        assert memo is not None
        assert memo["company_name"] == "Stripe"
        assert memo["rating"] == 9
        assert memo["recommendation"] == "Invest"

    def test_research_run_id_is_uuid(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        response = client.post("/api/research", json={"company_name": "Stripe"})
        body = _parse_sse_complete_event(response.text)
        run_id = body["research_run_id"]
        assert uuid.UUID(run_id)  # raises ValueError if not a valid UUID

    def test_different_requests_get_different_run_ids(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        r1 = _parse_sse_complete_event(client.post("/api/research", json={"company_name": "Stripe"}).text)
        r2 = _parse_sse_complete_event(client.post("/api/research", json={"company_name": "Stripe"}).text)
        assert r1["research_run_id"] != r2["research_run_id"]

    def test_empty_company_name_returns_422(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        response = client.post("/api/research", json={"company_name": ""})
        assert response.status_code == 422

    def test_missing_company_name_returns_422(self, client_with_mock_graph):
        client, _ = client_with_mock_graph
        response = client.post("/api/research", json={})
        assert response.status_code == 422

    def test_graph_failure_returns_sse_error(self, client_with_error_graph):
        response = client_with_error_graph.post("/api/research", json={"company_name": "Stripe"})
        assert response.status_code == 200 # SSE stream returns 200 before failure
        assert "error" in response.text
        assert "Simulated graph failure" in response.text
