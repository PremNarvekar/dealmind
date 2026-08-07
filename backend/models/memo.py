from pydantic import BaseModel , Field 
from typing import List 
from enum import Enum


class Recommendation(str, Enum):
    
    INVEST = "Invest",
    WATCH = "Watch",
    PASS = "Pass"

class MarketResult(BaseModel):
    market_size: str = Field(description="Estimated market size")
    competitors: List[str] = Field(default_factory=list)
    recent_news: List[str]= Field(default_factory=list)
    summary: str
    
class TeamResult(BaseModel):
    founders: List(str) = Field(default_factory=list)
    previous_companies:List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    summary: str
    
    
class ProductResult(BaseModel):
    product_name: str
    tech_stack: List(str) = Field(default_factory=list)
    differentiators:LIst(str) = Field(default_factory=list)
    strengths: List(str) = Field(default_factory=list)
    weakness: List(str) = Field(default_factory=list)
    summary: str

class InvestmentMemo(BaseModel):
    company_name: str
    market: MarketResult
    team: TeamResult
    product: ProductResult
    
    risks: List[str] = Field(default_factory=list)
    rating: int = Field(
        ge=1,
        le=10,
        description="Investment rating from 1 to 10"
    )
    
    recommendation: Recommendation
    
    executive_summary: str
        
    