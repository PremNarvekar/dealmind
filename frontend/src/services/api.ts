import type { ResearchRequest, ResearchResponse } from "../types";

const API_BASE_URL = "/api";

export const api = {
  /**
   * Triggers the LangGraph backend to research a company.
   * Note: This is a long-polling synchronous request that may take 30-60 seconds.
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

    const reader = response.body.getReader();
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
        buffer = parts.pop() || ""; // Keep the incomplete part in the buffer

        for (const part of parts) {
          if (part.startsWith("data: ")) {
            const dataStr = part.substring(6);
            try {
              const data = JSON.parse(dataStr);
              
              if (data.type === "complete") {
                finalResult = data.result;
              } else if (data.type === "error") {
                throw new Error(data.error);
              } else {
                // Call the progress callback if provided
                if (onProgress) {
                  onProgress(data);
                }
              }
            } catch (err) {
              console.error("Failed to parse SSE data:", err);
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
      throw new Error(`API Error: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("No readable stream returned from API.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const events = chunk.split("\n\n").filter(Boolean);

        for (const ev of events) {
          if (ev.startsWith("data: ")) {
            const dataStr = ev.substring(6);
            try {
              const data = JSON.parse(dataStr);
              if (onProgress) {
                onProgress(data);
              }
              if (data.type === "complete") {
                return data.result as ResearchResponse;
              }
              if (data.type === "error") {
                throw new Error(data.error);
              }
            } catch (err: any) {
              if (err.message !== "Unexpected end of JSON input") {
                console.error("Failed to parse SSE JSON:", err);
              }
            }
          }
        }
      }
      throw new Error("Stream closed before completion.");
    } finally {
      reader.releaseLock();
    }
  },
};
