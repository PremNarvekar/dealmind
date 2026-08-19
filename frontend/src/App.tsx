import { useState } from "react"
import { Layout } from "./components/layout/Layout"
import { ResearchForm } from "./components/ResearchForm"
import { ResultsView } from "./components/ResultsView"
import type { ResearchResponse } from "./types"
import { Alert } from "./components/ui/Alert"
import { Button } from "./components/ui/Button"
import { Spinner } from "./components/ui/Spinner"
import { api } from "./services/api"

export type Page = "research" | "memos" | "apikeys" | "settings"

function App() {
  const [page, setPage] = useState<Page>("research")
  const [result, setResult] = useState<ResearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isApproving, setIsApproving] = useState(false)

  const handleStart = () => {
    setError(null)
    setResult(null)
  }

  const handleSuccess = (data: ResearchResponse) => {
    setResult(data)
  }

  const handleError = (err: string) => {
    setError(err)
  }

  const handleApprove = async () => {
    if (!result || !result.research_run_id) return;
    setIsApproving(true);
    setError(null);
    try {
      const approvedResult = await api.approveResearch(result.research_run_id);
      setResult(approvedResult);
    } catch (err: any) {
      setError(err.message || "Approval failed. Please try again.");
    } finally {
      setIsApproving(false);
    }
  }

  return (
    <Layout activePage={page} onNavigate={setPage}>
      <div className="space-y-12">

        {/* ── Research Desk ── */}
        {page === "research" && (
          <>
            {!result && (
              <ResearchForm 
                onStart={handleStart} 
                onSuccess={handleSuccess} 
                onError={handleError} 
              />
            )}
            
            {error && (
              <div className="max-w-2xl mx-auto animate-slide-up">
                <Alert variant="danger" title="Research Failed" description={error} />
                <div className="text-center mt-4">
                  <button 
                    onClick={handleStart}
                    className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
                  >
                    Try again
                  </button>
                </div>
              </div>
            )}

            {result?.error && (
              <div className="max-w-2xl mx-auto animate-slide-up">
                <Alert variant="warning" title="Agent Warning" description={result.error} />
              </div>
            )}

            {result?.status === "needs_approval" && !result.investment_memo && (
              <div className="max-w-xl mx-auto p-10 bg-white/70 backdrop-blur-xl border border-border/50 rounded-2xl shadow-premium text-center animate-slide-up mt-24">
                <h3 className="text-2xl font-bold tracking-tight-premium mb-3 text-primary">Research Phase Complete</h3>
                <p className="text-muted-foreground mb-8 leading-relaxed">
                  The AI agents have finished gathering raw data on <strong>{result.company_name}</strong>. You may now approve the data to synthesize the final investment memo.
                </p>
                <Button
                  onClick={handleApprove}
                  disabled={isApproving}
                  className="px-10 py-6 h-auto text-base rounded-xl font-medium shadow-sm transition-all hover:scale-[1.02]"
                >
                  {isApproving ? (
                    <>
                      <Spinner className="mr-2 h-4 w-4" />
                      Generating Memo…
                    </>
                  ) : (
                    "Approve & Generate Memo"
                  )}
                </Button>
              </div>
            )}

            {result?.investment_memo && (
              <div className="animate-slide-up">
                <ResultsView memo={result.investment_memo} />
              </div>
            )}

            {result && (
              <div className="mt-16 pb-12 text-center animate-slide-up">
                <button 
                  onClick={handleStart}
                  className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors border-b border-transparent hover:border-primary pb-0.5"
                >
                  Start a new research deep-dive
                </button>
              </div>
            )}
          </>
        )}

        {/* ── Investment Memos ── */}
        {page === "memos" && (
          <div className="max-w-2xl mx-auto mt-20 text-center animate-slide-up">
            <h2 className="text-3xl font-semibold tracking-tight-premium text-primary mb-4">Investment Memos</h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              Investment memos are generated in real-time when you complete a research run on the Research Desk.
            </p>
            <p className="text-sm text-muted-foreground">
              The backend does not currently support memo storage or retrieval. Each memo is generated fresh per research session.
            </p>
            <div className="mt-8">
              <Button
                onClick={() => setPage("research")}
                className="px-8 py-4 h-auto text-base rounded-xl"
              >
                Go to Research Desk
              </Button>
            </div>
          </div>
        )}

        {/* ── API Keys ── */}
        {page === "apikeys" && (
          <div className="max-w-2xl mx-auto mt-20 text-center animate-slide-up">
            <h2 className="text-3xl font-semibold tracking-tight-premium text-primary mb-4">API Keys</h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              DealMind uses <strong>Google Gemini</strong> and <strong>Tavily</strong> APIs for research. 
              API keys are configured server-side via environment variables and are never exposed to the browser.
            </p>
            <div className="mt-8 p-6 bg-white rounded-2xl border border-border/50 shadow-sm text-left space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-foreground">GOOGLE_API_KEY</span>
                <span className="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-md font-medium">Server-side</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-foreground">TAVILY_API_KEY</span>
                <span className="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-md font-medium">Server-side</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-foreground">DATABASE_URL</span>
                <span className="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-md font-medium">Server-side</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              To update API keys, modify the environment variables in your deployment platform (Render, Docker, or Kubernetes).
            </p>
          </div>
        )}

        {/* ── Settings ── */}
        {page === "settings" && (
          <div className="max-w-2xl mx-auto mt-20 text-center animate-slide-up">
            <h2 className="text-3xl font-semibold tracking-tight-premium text-primary mb-4">Settings</h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              DealMind configuration is managed server-side. The current system settings are:
            </p>
            <div className="mt-8 p-6 bg-white rounded-2xl border border-border/50 shadow-sm text-left space-y-4">
              <div className="flex items-center justify-between py-2 border-b border-border/30">
                <span className="text-sm font-medium text-foreground">LLM Model</span>
                <span className="text-sm text-muted-foreground">Google Gemini (configurable via GEMINI_MODEL)</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-border/30">
                <span className="text-sm font-medium text-foreground">Search Provider</span>
                <span className="text-sm text-muted-foreground">Tavily</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-border/30">
                <span className="text-sm font-medium text-foreground">Agent Architecture</span>
                <span className="text-sm text-muted-foreground">LangGraph Supervisor + 3 Specialists</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm font-medium text-foreground">Human-in-the-Loop</span>
                <span className="text-sm text-muted-foreground">Enabled (approve before memo synthesis)</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              To modify settings, update the backend environment variables and redeploy.
            </p>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default App
