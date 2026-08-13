export type Recommendation = "Invest" | "Watch" | "Pass";

export interface MarketResult {
  market_size: string;
  competitors: string[];
  recent_news: string[];
  summary: string;
}

export interface TeamResult {
  founders: string[];
  previous_companies: string[];
  strengths: string[];
  concerns: string[];
  summary: string;
}

export interface ProductResult {
  product_name: string;
  tech_stack: string[];
  differentiators: string[];
  strengths: string[];
  weakness: string[];
  summary: string;
}

export interface InvestmentMemo {
  company_name: string;
  market: MarketResult;
  team: TeamResult;
  product: ProductResult;
  risks: string[];
  rating: number; // 1 to 10
  recommendation: Recommendation;
  executive_summary: string;
  missing_information?: string[];
}

export interface ResearchRequest {
  company_name: string;
  selected_agents: string[];
}

export interface ResearchResponse {
  research_run_id: string;
  company_name: string;
  status: string;
  investment_memo?: InvestmentMemo;
  error?: string;
}
