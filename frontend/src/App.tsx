import { useState } from "react"
import { Layout } from "./components/layout/Layout"
import { ResearchForm } from "./components/ResearchForm"
import { ResultsView } from "./components/ResultsView"
import type { ResearchResponse } from "./types"
import { Alert } from "./components/ui/Alert"
import { Button } from "./components/ui/Button"


function App() {
  const [result, setResult] = useState<ResearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

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
    try {
      setResult(null); // Clear to show loading state if desired, or keep and add a loading spinner
      // But it's better to keep result and just show a spinner. 
      // We'll manage a local loading state.
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <Layout>
      <div className="space-y-12">
        {/* Only show the form if we don't have a successful result yet, or we could keep it to allow a new search */}
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
          </div>
        )}

        {result?.error && (
          <div className="max-w-2xl mx-auto animate-slide-up">
            <Alert variant="warning" title="Agent Warning" description={result.error} />
          </div>
        )}

        {result?.status === "needs_approval" && (
          <div className="max-w-xl mx-auto p-10 bg-white/70 backdrop-blur-xl border border-border/50 rounded-2xl shadow-premium text-center animate-slide-up mt-24">
            <h3 className="text-2xl font-bold tracking-tight-premium mb-3 text-primary">Research Phase Complete</h3>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              The AI agents have finished gathering raw data on {result.company_name}. You may now approve the data to synthesize the final investment memo.
            </p>
            <Button
              onClick={handleApprove}
              className="px-10 py-6 h-auto text-base rounded-xl font-medium shadow-sm transition-all hover:scale-[1.02]"
            >
              Approve & Generate Memo
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
      </div>
    </Layout>
  )
}

export default App
