import { useState } from "react"
import type { InvestmentMemo } from "../types"
import { Badge } from "./ui/Badge"
import { AlertCircle, CheckCircle2, AlertTriangle } from "lucide-react"

interface ResultsViewProps {
  memo: InvestmentMemo
}

type TabType = "summary" | "market" | "team" | "product"

export function ResultsView({ memo }: ResultsViewProps) {
  const [activeTab, setActiveTab] = useState<TabType>("summary")

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case "Invest": return <Badge variant="success" className="text-xs px-3 py-1 font-semibold uppercase tracking-wider">Strong Buy (Invest)</Badge>
      case "Watch": return <Badge variant="warning" className="text-xs px-3 py-1 font-semibold uppercase tracking-wider">Hold (Watch)</Badge>
      default: return <Badge variant="danger" className="text-xs px-3 py-1 font-semibold uppercase tracking-wider">Pass (Do Not Invest)</Badge>
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return "text-green-700 bg-green-50 border-green-200"
    if (score >= 5) return "text-amber-700 bg-amber-50 border-amber-200"
    return "text-red-700 bg-red-50 border-red-200"
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-12 fade-in mt-8 bg-white p-8 md:p-12 shadow-premium rounded-xl">
      {/* Header Profile */}
      <header className="border-b border-border/60 pb-10">
        <h1 className="text-5xl font-bold text-primary mb-6 tracking-tight-premium">
          {memo.company_name}
        </h1>
        <div className="flex items-center space-x-4">
          {getRecommendationBadge(memo.recommendation)}
          <div className={`px-4 py-1.5 rounded-md border text-sm font-bold ${getScoreColor(memo.rating)}`}>
            Conviction Score: {memo.rating}/10
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="flex space-x-6 border-b border-border/40 pb-[1px]">
        <TabButton active={activeTab === "summary"} onClick={() => setActiveTab("summary")}>
          Executive Summary
        </TabButton>
        <TabButton active={activeTab === "market"} onClick={() => setActiveTab("market")}>
          Market
        </TabButton>
        <TabButton active={activeTab === "team"} onClick={() => setActiveTab("team")}>
          Team
        </TabButton>
        <TabButton active={activeTab === "product"} onClick={() => setActiveTab("product")}>
          Product
        </TabButton>
      </nav>

      {/* Tab Content */}
      <main className="py-2 min-h-[400px]">
        {activeTab === "summary" && <SummaryTab memo={memo} />}
        {activeTab === "market" && <MarketTab market={memo.market} />}
        {activeTab === "team" && <TeamTab team={memo.team} />}
        {activeTab === "product" && <ProductTab product={memo.product} />}
      </main>
    </div>
  )
}

function TabButton({ active, onClick, children }: any) {
  return (
    <button
      onClick={onClick}
      className={`pb-4 text-sm font-medium transition-all duration-300 relative ${
        active 
          ? "text-primary" 
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {children}
      {active && (
        <span className="absolute bottom-0 left-0 w-full h-[2px] bg-primary rounded-t-full" />
      )}
    </button>
  )
}

function SummaryTab({ memo }: { memo: InvestmentMemo }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 animate-slide-up">
      <div className="col-span-1 lg:col-span-2 prose-premium">
        <h3>Investment Thesis</h3>
        <p className="whitespace-pre-wrap">{memo.executive_summary}</p>
      </div>
      
      <div className="space-y-10">
        <div>
          <h4 className="flex items-center text-sm font-semibold uppercase tracking-wider text-red-700 mb-4">
            <AlertTriangle className="mr-2 h-4 w-4" /> Key Risks
          </h4>
          <ul className="space-y-3">
            {memo.risks.map((risk, i) => (
              <li key={i} className="flex items-start text-sm text-foreground/80 leading-relaxed">
                <span className="mr-3 text-red-500 mt-1 flex-shrink-0">—</span>
                <span>{risk}</span>
              </li>
            ))}
            {memo.risks.length === 0 && <span className="text-sm text-muted-foreground italic">None identified.</span>}
          </ul>
        </div>
        
        {memo.missing_information && memo.missing_information.length > 0 && (
          <div>
            <h4 className="flex items-center text-sm font-semibold uppercase tracking-wider text-amber-700 mb-4">
              <AlertCircle className="mr-2 h-4 w-4" /> Missing Info
            </h4>
            <ul className="space-y-3 border-l-2 border-amber-200 pl-4">
              {memo.missing_information.map((info, i) => (
                <li key={i} className="text-sm text-muted-foreground leading-relaxed">{info}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

function MarketTab({ market }: { market: InvestmentMemo["market"] }) {
  return (
    <div className="prose-premium animate-slide-up space-y-10">
      <div>
        <h3>Market Analysis</h3>
        <p className="whitespace-pre-wrap">{market.summary}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 pt-6 border-t border-border/40">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Total Addressable Market</h4>
          <div className="text-3xl font-light tracking-tight-premium text-primary">{market.market_size}</div>
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">Key Competitors</h4>
          <div className="flex flex-wrap gap-2">
            {market.competitors.map((comp, i) => (
              <span key={i} className="px-3 py-1 bg-muted text-muted-foreground text-sm rounded-md border border-border/50">{comp}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function TeamTab({ team }: { team: InvestmentMemo["team"] }) {
  return (
    <div className="prose-premium animate-slide-up space-y-10">
      <div>
        <h3>Team Evaluation</h3>
        <p className="whitespace-pre-wrap">{team.summary}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 pt-6 border-t border-border/40">
        <div>
          <h4 className="flex items-center text-sm font-semibold uppercase tracking-wider text-green-700 mb-4">
            <CheckCircle2 className="mr-2 h-4 w-4"/> Strengths
          </h4>
          <ul className="space-y-3">
            {team.strengths.map((s, i) => (
              <li key={i} className="flex items-start text-sm text-foreground/80 leading-relaxed">
                <span className="mr-3 text-green-500 flex-shrink-0">—</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="flex items-center text-sm font-semibold uppercase tracking-wider text-amber-700 mb-4">
            <AlertCircle className="mr-2 h-4 w-4"/> Concerns
          </h4>
          <ul className="space-y-3">
            {team.concerns.map((c, i) => (
              <li key={i} className="flex items-start text-sm text-foreground/80 leading-relaxed">
                <span className="mr-3 text-amber-500 flex-shrink-0">—</span>
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

function ProductTab({ product }: { product: InvestmentMemo["product"] }) {
  return (
    <div className="prose-premium animate-slide-up space-y-10">
      <div>
        <h3>Product Overview <span className="text-muted-foreground font-normal ml-2">/ {product.product_name}</span></h3>
        <p className="whitespace-pre-wrap">{product.summary}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 pt-6 border-t border-border/40">
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wider text-primary mb-4">Differentiators</h4>
          <ul className="space-y-3">
            {product.differentiators.map((d, i) => (
              <li key={i} className="flex items-start text-sm text-foreground/80 leading-relaxed">
                <span className="mr-3 text-primary/40 flex-shrink-0">—</span>
                <span>{d}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Weaknesses</h4>
          <ul className="space-y-3">
            {product.weakness.map((w, i) => (
              <li key={i} className="flex items-start text-sm text-foreground/80 leading-relaxed">
                <span className="mr-3 text-muted-foreground/40 flex-shrink-0">—</span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="pt-6 border-t border-border/40">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">Technology Stack</h4>
        <div className="flex flex-wrap gap-2">
          {product.tech_stack.map((t, i) => (
            <span key={i} className="px-3 py-1 bg-white text-primary text-sm rounded-md border shadow-sm">{t}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
