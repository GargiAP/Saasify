import { AnalysisResult } from "@/types/analysis";

export async function analyzeIdea(idea: string): Promise<AnalysisResult> {
  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ idea }),
  });

  if (!response.ok) {
    throw new Error("Analysis failed");
  }

  return response.json();
}