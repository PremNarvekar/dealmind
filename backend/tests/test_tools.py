"""
test_tools.py — Tests for Tavily search tools (mocked).
"""
from unittest.mock import patch, MagicMock

import pytest


class TestMarketTools:
    def test_search_market_size_invokes_tavily(self, mock_tavily_response):
        with patch("tools.market_tools.tavily_search") as mock_tavily:
            mock_tavily.invoke.return_value = mock_tavily_response
            from tools.market_tools import search_market_size
            result = search_market_size.invoke({"company_name": "Stripe"})
            mock_tavily.invoke.assert_called_once()
            call_args = mock_tavily.invoke.call_args[0][0]
            assert "Stripe" in call_args["query"]

    def test_search_competitors_invokes_tavily(self, mock_tavily_response):
        with patch("tools.market_tools.tavily_search") as mock_tavily:
            mock_tavily.invoke.return_value = mock_tavily_response
            from tools.market_tools import search_competitors
            result = search_competitors.invoke({"company_name": "Stripe"})
            mock_tavily.invoke.assert_called_once()

    def test_search_recent_news_invokes_tavily(self, mock_tavily_response):
        with patch("tools.market_tools.tavily_search") as mock_tavily:
            mock_tavily.invoke.return_value = mock_tavily_response
            from tools.market_tools import search_recent_news
            result = search_recent_news.invoke({"company_name": "Stripe"})
            mock_tavily.invoke.assert_called_once()

    def test_market_tools_are_decorated_with_tool(self):
        """Verify tools are decorated with @tool so they have name/description."""
        from tools.market_tools import search_market_size, search_competitors, search_recent_news
        assert hasattr(search_market_size, "name")
        assert hasattr(search_competitors, "name")
        assert hasattr(search_recent_news, "name")


class TestTeamTools:
    def test_search_founder_profile_invokes_tavily(self, mock_tavily_response):
        with patch("tools.team_tools.tavily_search") as mock_tavily:
            mock_tavily.invoke.return_value = mock_tavily_response
            from tools.team_tools import search_founder_profile
            result = search_founder_profile.invoke({"company_name": "Stripe"})
            mock_tavily.invoke.assert_called_once()

    def test_team_tools_are_decorated_with_tool(self):
        from tools.team_tools import search_founder_profile, search_founder_history, search_team_strengths_concerns
        for tool in [search_founder_profile, search_founder_history, search_team_strengths_concerns]:
            assert hasattr(tool, "name"), f"{tool} is not decorated with @tool"


class TestProductTools:
    def test_search_product_name_invokes_tavily(self, mock_tavily_response):
        with patch("tools.product_tools.tavily_search") as mock_tavily:
            mock_tavily.invoke.return_value = mock_tavily_response
            from tools.product_tools import search_product_name
            result = search_product_name.invoke({"company_name": "Stripe"})
            mock_tavily.invoke.assert_called_once()

    def test_product_tools_are_decorated_with_tool(self):
        from tools.product_tools import search_product_name, search_tech_stack, search_products_strengths_concerns
        for tool in [search_product_name, search_tech_stack, search_products_strengths_concerns]:
            assert hasattr(tool, "name"), f"{tool} is not decorated with @tool"
