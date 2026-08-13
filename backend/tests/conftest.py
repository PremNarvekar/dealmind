"""
conftest.py — shared pytest fixtures and mocks.

All fixtures that mock external APIs (Tavily, Gemini, PostgreSQL) live here
so unit tests require no real credentials.
"""
import os
import sys
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# ── Ensure backend/ is on sys.path ──────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Provide fake env vars BEFORE importing config ───────────────────────────
os.environ.setdefault("GOOGLE_API_KEY", "fake-google-key-for-tests")
os.environ.setdefault("TAVILY_API_KEY", "fake-tavily-key-for-tests")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
os.environ.setdefault("GEMINI_MODEL", "gemini-2.0-flash")


@pytest.fixture
def sample_market_result():
    from models.memo import MarketResult
    return MarketResult(
        market_size="$100B TAM",
        competitors=["Adyen", "Braintree", "Square"],
        recent_news=["Stripe raised Series X at $95B valuation"],
        summary="Stripe operates in a large and growing payments market.",
    )


@pytest.fixture
def sample_team_result():
    from models.memo import TeamResult
    return TeamResult(
        founders=["Patrick Collison (CEO)", "John Collison (President)"],
        previous_companies=["Auctomatic"],
        strengths=["Proven founders", "Deep technical expertise", "Strong network"],
        concerns=["Heavy reliance on key founders"],
        summary="Strong founding team with proven track record.",
    )


@pytest.fixture
def sample_product_result():
    from models.memo import ProductResult
    return ProductResult(
        product_name="Stripe Payments API",
        tech_stack=["Python", "Ruby", "Java SDKs", "REST API"],
        differentiators=["Developer-first design", "Comprehensive API", "Global coverage"],
        strengths=["Industry-leading developer experience", "High reliability"],
        weakness=["Complex pricing", "Less SMB-focused than Square"],
        summary="Best-in-class payments API with strong developer adoption.",
    )


@pytest.fixture
def sample_investment_memo(sample_market_result, sample_team_result, sample_product_result):
    from models.memo import InvestmentMemo, Recommendation
    return InvestmentMemo(
        company_name="Stripe",
        market=sample_market_result,
        team=sample_team_result,
        product=sample_product_result,
        risks=["Regulatory risk", "Competition from incumbents"],
        rating=9,
        recommendation=Recommendation.INVEST,
        executive_summary="Stripe is a strong investment with a dominant market position.",
        missing_information=[],
    )


@pytest.fixture
def mock_tavily_response():
    return {
        "query": "test query",
        "results": [
            {
                "url": "https://example.com",
                "title": "Example Result",
                "content": "This is a test result.",
                "score": 0.95,
            }
        ],
    }


@pytest.fixture
def mock_checkpointer():
    """Returns a MagicMock that behaves like a PostgresSaver."""
    checkpointer = MagicMock()
    checkpointer.setup.return_value = None
    return checkpointer
