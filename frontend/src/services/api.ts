import type { ResearchRequest, ResearchResponse } from "../types";

const API_BASE_URL = "https://dealmind-wjhm.onrender.com/api";

export const api = {
  /**
   * Health check — verifies the production backend is reachable.
   */
  async healthCheck(): Promise<{ status: string; graph_ready: boolean }> {
    const response = await fetch(
      API_BASE_URL.replace("/api", "/health"),
      { signal: AbortSignal.timeout(15000) }
    );
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  },

  /**
   * Triggers the LangGraph backend to research a company.
   * Returns an SSE stream of progress events, then a final result.
   */
  async researchCompany(
    companyName: string,
    selectedAgents: string[],
    onProgress?: (event: any) => void
  ): Promise<ResearchResponse> {
    const response = await fetch(`${API_BASE_URL}/research`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
      },
      body: JSON.stringify({ 
        company_name: companyName,
        selected_agents: selectedAgents
      } as ResearchRequest),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `Server error: ${response.status} ${response.statusText}`
      );
    }

    if (!response.body) {
      throw new Error("Response body is empty or streaming is not supported.");
    }

    return this._readSSEStream(response.body, onProgress);
  },

  /**
   * Approves a paused research run to trigger memo synthesis.
   */
  async approveResearch(
    runId: string,
    onProgress?: (event: any) => void
  ): Promise<ResearchResponse> {
    const response = await fetch(`${API_BASE_URL}/research/${runId}/approve`, {
      method: "POST",
      headers: {
        "Accept": "text/event-stream",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `Approval failed: ${response.status} ${response.statusText}`
      );
    }

    if (!response.body) {
      throw new Error("No readable stream returned from API.");
    }

    return this._readSSEStream(response.body, onProgress);
  },

  /**
   * Shared SSE stream reader. Parses server-sent events and returns the
   * final ResearchResponse when a "complete" event is received.
   */
  async _readSSEStream(
    body: ReadableStream<Uint8Array>,
    onProgress?: (event: any) => void
  ): Promise<ResearchResponse> {
    const reader = body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let finalResult: ResearchResponse | null = null;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Split on SSE message boundaries
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          if (part.startsWith("data: ")) {
            const dataStr = part.substring(6);
            const data = JSON.parse(dataStr);

            if (data.type === "complete") {
              finalResult = data.result;
            } else if (data.type === "error") {
              throw new Error(data.error || "Backend returned an error.");
            } else {
              if (onProgress) {
                onProgress(data);
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    if (!finalResult) {
      throw new Error("Stream closed before completion.");
    }

    return finalResult;
  },
};
