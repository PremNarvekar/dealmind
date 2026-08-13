"""
test_models.py — Tests for Pydantic models in models/memo.py and models/state.py.
"""
import pytest
from pydantic import ValidationError

from models.memo import (
    Recommendation,
    MarketResult,
    TeamResult,
    ProductResult,
    InvestmentMemo,
)


class TestRecommendation:
    def test_invest_value(self):
        assert Recommendation.INVEST == "Invest"

    def test_watch_value(self):
        assert Recommendation.WATCH == "Watch"

    def test_pass_value(self):
        assert Recommendation.PASS == "Pass"

    def test_invest_is_not_tuple(self):
        """Regression test: the original code had INVEST = 'Invest', (trailing comma = tuple)."""
        assert not isinstance(Recommendation.INVEST.value, tuple)


class TestMarketResult:
    def test_basic_creation(self, sample_market_result):
        assert sample_market_result.market_size == "$100B TAM"
        assert len(sample_market_result.competitors) == 3
        assert sample_market_result.summary

    def test_defaults_are_lists(self):
        m = MarketResult(market_size="large", summary="ok")
        assert m.competitors == []
        assert m.recent_news == []

    def test_json_roundtrip(self, sample_market_result):
        json_str = sample_market_result.model_dump_json()
        restored = MarketResult.model_validate_json(json_str)
        assert restored == sample_market_result


class TestTeamResult:
    def test_basic_creation(self, sample_team_result):
        assert "Patrick Collison (CEO)" in sample_team_result.founders
        assert sample_team_result.summary

    def test_defaults_are_lists(self):
        t = TeamResult(summary="ok")
        assert t.founders == []
        assert t.concerns == []


class TestProductResult:
    def test_basic_creation(self, sample_product_result):
        assert sample_product_result.product_name == "Stripe Payments API"
        assert sample_product_result.summary

    def test_defaults_are_lists(self):
        p = ProductResult(product_name="Test Product", summary="ok")
        assert p.tech_stack == []
        assert p.weakness == []


class TestInvestmentMemo:
    def test_basic_creation(self, sample_investment_memo):
        assert sample_investment_memo.company_name == "Stripe"
        assert sample_investment_memo.rating == 9
        assert sample_investment_memo.recommendation == Recommendation.INVEST

    def test_rating_bounds(self, sample_market_result, sample_team_result, sample_product_result):
        with pytest.raises(ValidationError):
            InvestmentMemo(
                company_name="X",
                market=sample_market_result,
                team=sample_team_result,
                product=sample_product_result,
                rating=11,  # out of range
                recommendation=Recommendation.INVEST,
                executive_summary="test",
            )

    def test_rating_lower_bound(self, sample_market_result, sample_team_result, sample_product_result):
        with pytest.raises(ValidationError):
            InvestmentMemo(
                company_name="X",
                market=sample_market_result,
                team=sample_team_result,
                product=sample_product_result,
                rating=0,  # out of range
                recommendation=Recommendation.PASS,
                executive_summary="test",
            )

    def test_missing_information_defaults_to_empty(self, sample_investment_memo):
        assert sample_investment_memo.missing_information == []

    def test_json_roundtrip(self, sample_investment_memo):
        json_str = sample_investment_memo.model_dump_json()
        restored = InvestmentMemo.model_validate_json(json_str)
        assert restored.company_name == sample_investment_memo.company_name
        assert restored.rating == sample_investment_memo.rating


class TestGraphState:
    def test_state_is_typeddict(self):
        from models.state import GraphState
        # TypedDict classes have __annotations__
        assert hasattr(GraphState, "__annotations__")

    def test_state_has_required_fields(self):
        from models.state import GraphState
        annotations = GraphState.__annotations__
        required = [
            "company_name", "thread_id", "messages",
            "market", "team", "product", "investment_memo",
            "approved", "auto_approve", "status", "error",
        ]
        for field in required:
            assert field in annotations, f"GraphState missing field: {field}"

    def test_messages_has_add_messages_reducer(self):
        """Verify messages field uses add_messages annotation for LangGraph.

        Note: from __future__ import annotations (PEP 563) makes annotations
        lazy strings at runtime. We resolve them with get_type_hints().
        """
        import typing
        from models.state import GraphState

        # Resolve string annotations to actual types
        hints = typing.get_type_hints(GraphState, include_extras=True)
        messages_annotation = hints["messages"]
        # Annotated types carry __metadata__
        origin = getattr(messages_annotation, "__metadata__", None)
        assert origin is not None, "messages field must be Annotated with add_messages"
