from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class Recommendation(str, Enum):
    INVEST = "Invest"
    WATCH = "Watch"
    PASS = "Pass"


class MarketResult(BaseModel):
    market_size: str = Field(description="Estimated market size (TAM/SAM/SOM where available)")
    competitors: List[str] = Field(default_factory=list, description="Main competitors")
    recent_news: List[str] = Field(default_factory=list, description="Recent relevant news items")
    summary: str = Field(description="Market research summary")


class TeamResult(BaseModel):
    founders: List[str] = Field(default_factory=list, description="Founder names and roles")
    previous_companies: List[str] = Field(default_factory=list, description="Previous companies founded or worked at")
    strengths: List[str] = Field(default_factory=list, description="Team strengths")
    concerns: List[str] = Field(default_factory=list, description="Team concerns or gaps")
    summary: str = Field(description="Team research summary")


class ProductResult(BaseModel):
    product_name: str = Field(description="Name of the primary product or service")
    tech_stack: List[str] = Field(default_factory=list, description="Known technology stack")
    differentiators: List[str] = Field(default_factory=list, description="Key product differentiators")
    strengths: List[str] = Field(default_factory=list, description="Product strengths")
    weakness: List[str] = Field(default_factory=list, description="Product weaknesses or gaps")
    summary: str = Field(description="Product research summary")


class InvestmentMemo(BaseModel):
    company_name: str = Field(description="Name of the company being researched")
    market: MarketResult = Field(description="Market research results")
    team: TeamResult = Field(description="Team research results")
    product: ProductResult = Field(description="Product research results")
    risks: List[str] = Field(default_factory=list, description="Key investment risks")
    rating: int = Field(ge=1, le=10, description="Investment rating from 1 (avoid) to 10 (strong buy)")
    recommendation: Recommendation = Field(description="Final investment recommendation")
    executive_summary: str = Field(description="Executive summary of the investment thesis")
    missing_information: Optional[List[str]] = Field(
        default_factory=list,
        description="Areas where information was unavailable or unreliable"
    )