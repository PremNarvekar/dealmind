import { useState } from "react";
import { Search, CheckCircle2, CircleDashed } from "lucide-react";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";

import { Spinner } from "./ui/Spinner";
import { api } from "../services/api";
import type { ResearchResponse } from "../types";

interface ResearchFormProps {
  onStart: () => void;
  onSuccess: (data: ResearchResponse) => void;
  onError: (error: string) => void;
}

export function ResearchForm({ onStart, onSuccess, onError }: ResearchFormProps) {
  const [companyName, setCompanyName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState<string[]>([]);
  const [selectedAgents, setSelectedAgents] = useState<string[]>(["market", "team", "product"]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim() || isLoading) return;

    try {
      setIsLoading(true);
      setEvents([]);
      onStart();
      
      const result = await api.researchCompany(
        companyName.trim(), 
        selectedAgents,
        (event) => {
        if (event.type === 'start') {
          setEvents(prev => [...prev, 'Initialized research run...']);
        } else if (event.type === 'node_update' && event.node) {
          const formattedNode = event.node.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
          setEvents(prev => [...prev, `${formattedNode} completed.`]);
        }
      });
      onSuccess(result);
    } catch (err: any) {
      onError(err.message || "An unexpected error occurred during research.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-20 fade-in px-4">
      <div className="mb-10 text-center animate-slide-up">
        <h2 className="text-4xl font-semibold tracking-tight-premium text-primary mb-3">
          DealMind AI
        </h2>
        <p className="text-muted-foreground text-lg font-light tracking-wide">
          Enter a startup name to trigger a multi-agent deep dive.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="relative flex items-center w-full animate-slide-up" style={{ animationDelay: '100ms' }}>
        <Search className="absolute left-6 w-5 h-5 text-muted-foreground" />
        <Input
          className="pl-14 pr-36 h-16 text-lg bg-white shadow-premium border-transparent rounded-2xl focus-visible:ring-1 focus-visible:ring-primary/20 transition-all"
          placeholder="e.g. Stripe, Vercel, Anthropic..."
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          disabled={isLoading}
          autoFocus
        />
        <div className="absolute right-2 flex items-center h-full">
          <Button 
            type="submit" 
            className="h-12 px-8 rounded-xl font-medium shadow-sm"
            disabled={!companyName.trim() || isLoading || selectedAgents.length === 0}
          >
            {isLoading ? (
              <>
                <Spinner className="mr-2 h-4 w-4" />
                Analyzing
              </>
            ) : (
              "Analyze"
            )}
          </Button>
        </div>
      </form>

      <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm text-muted-foreground animate-slide-up" style={{ animationDelay: '200ms' }}>
        <span className="font-medium">Research Scope:</span>
        {["market", "team", "product"].map((agent) => (
          <label key={agent} className="flex items-center space-x-2 cursor-pointer group">
            <input 
              type="checkbox"
              className="rounded-sm border-border text-primary focus:ring-primary h-4 w-4 transition-colors"
              checked={selectedAgents.includes(agent)}
              onChange={(e) => {
                if (e.target.checked) {
                  setSelectedAgents(prev => [...prev, agent]);
                } else {
                  setSelectedAgents(prev => prev.filter(a => a !== agent));
                }
              }}
              disabled={isLoading}
            />
            <span className="capitalize group-hover:text-foreground transition-colors">{agent}</span>
          </label>
        ))}
      </div>
      
      {isLoading && (
        <div className="mt-12 p-6 rounded-2xl glass-panel animate-slide-up">
          <div className="space-y-4">
            {events.map((event, idx) => (
              <div key={idx} className="flex items-center text-muted-foreground animate-in fade-in slide-in-from-bottom-2 duration-500">
                <CheckCircle2 className="w-4 h-4 mr-3 text-success" />
                <span className="text-sm">{event}</span>
              </div>
            ))}
            <div className="flex items-center text-primary font-medium text-sm pt-2">
              <CircleDashed className="w-4 h-4 mr-3 animate-spin text-primary" />
              Processing next step...
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
