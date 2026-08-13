"""
test_graph.py — Tests for graph nodes and state flow (all external APIs mocked).
"""
from unittest.mock import MagicMock, patch
import pytest


class TestExtractResultsNode:
    """Tests for the extract_results_node in graph.py."""

    def test_extracts_market_from_additional_kwargs(self, sample_market_result):
        """Verify extraction from message.additional_kwargs['structured_response']."""
        from langchain_core.messages import AIMessage
        from graph.graph import extract_results_node

        msg = AIMessage(
            content="Market research complete.",
            name="market_agent",
            additional_kwargs={"structured_response": sample_market_result.model_dump()},
        )

        state = {
            "company_name": "Stripe",
            "thread_id": "test-run-id",
            "messages": [msg],
            "market": None,
            "team": None,
            "product": None,
        }

        result = extract_results_node(state)
        assert result["market"] is not None
        assert result["market"].market_size == "$100B TAM"

    def test_placeholder_when_no_market_message(self):
        """When no agent message found, a placeholder MarketResult is created."""
        from graph.graph import extract_results_node
        from langchain_core.messages import HumanMessage

        state = {
            "company_name": "Stripe",
            "thread_id": "test-run-id",
            "messages": [HumanMessage(content="Research Stripe")],
            "market": None,
            "team": None,
            "product": None,
        }

        result = extract_results_node(state)
        assert result["market"] is not None
        assert "unavailable" in result["market"].market_size.lower() or "not captured" in result["market"].summary.lower()


class TestValidateResearchNode:
    def test_sets_status_to_synthesizing(self, sample_market_result, sample_team_result, sample_product_result):
        from graph.graph import validate_research_node

        state = {
            "company_name": "Stripe",
            "thread_id": "test-run-id",
            "market": sample_market_result,
            "team": sample_team_result,
            "product": sample_product_result,
        }
        result = validate_research_node(state)
        assert result["status"] == "needs_approval"


class TestSynthesizeMemoNode:
    def test_produces_investment_memo(
        self, sample_market_result, sample_team_result, sample_product_result, sample_investment_memo
    ):
        """synthesis_memo_node should call LLM and return investment_memo."""
        from graph.graph import synthesize_memo_node
        import graph.graph as graph_module

        original_llm = graph_module._synthesis_llm_structured
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = sample_investment_memo
        graph_module._synthesis_llm_structured = mock_llm

        try:
            state = {
                "company_name": "Stripe",
                "thread_id": "test-run-id",
                "market": sample_market_result,
                "team": sample_team_result,
                "product": sample_product_result,
            }
            result = synthesize_memo_node(state)
        finally:
            graph_module._synthesis_llm_structured = original_llm

        assert result["status"] == "complete"
        assert result["investment_memo"] is not None
        assert result["investment_memo"].company_name == "Stripe"
        mock_llm.invoke.assert_called_once()

    def test_handles_synthesis_failure_gracefully(
        self, sample_market_result, sample_team_result, sample_product_result
    ):
        """When LLM fails, node returns error status rather than raising."""
        from graph.graph import synthesize_memo_node
        import graph.graph as graph_module

        original_llm = graph_module._synthesis_llm_structured
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = RuntimeError("LLM timeout")
        graph_module._synthesis_llm_structured = mock_llm

        try:
            state = {
                "company_name": "Stripe",
                "thread_id": "test-run-id",
                "market": sample_market_result,
                "team": sample_team_result,
                "product": sample_product_result,
            }
            result = synthesize_memo_node(state)
        finally:
            graph_module._synthesis_llm_structured = original_llm

        assert result["status"] == "error"
        assert "Synthesis failed" in result["error"]


class TestGraphState:
    def test_state_construction(self, sample_market_result):
        """Verify GraphState TypedDict accepts all expected fields."""
        from models.state import GraphState
        from langchain_core.messages import HumanMessage

        state: GraphState = {
            "company_name": "Stripe",
            "thread_id": "abc-123",
            "messages": [HumanMessage(content="test")],
            "market": sample_market_result,
            "team": None,
            "product": None,
            "investment_memo": None,
            "approved": False,
            "auto_approve": True,
            "status": "pending",
            "error": None,
        }
        assert state["company_name"] == "Stripe"
        assert state["thread_id"] == "abc-123"
