'use client';

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { analyzeIdea } from "@/services/mlService";
import { AnalysisResult } from "@/types/analysis";

export default function AnalyzePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const idea = searchParams.get("idea");

  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!idea) return;
    const run = async () => {
      try {
        const data = await analyzeIdea(idea);
        setResult(data);
      } catch (err) {
        setError("Analysis failed. Make sure the ML service is running.");
      }
      setLoading(false);
    };
    run();
  }, [idea]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] text-white flex flex-col items-center justify-center gap-4">
        <div className="h-10 w-10 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
        <p className="text-white/60 text-sm">Running ML pipeline...</p>
        <p className="text-white/30 text-xs">FAISS search → Gap analysis → Viability score → LLM report</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#020617] text-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-red-400">{error}</p>
          <button onClick={() => router.push("/")} className="text-cyan-400 hover:underline">
            ← Go back
          </button>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const crowdingColor = {
    High: "text-red-400",
    Medium: "text-yellow-400",
    Low: "text-green-400"
  }[result.gap_analysis.crowding_level] ?? "text-white";

  const scoreColor = result.viability.score >= 60
    ? "text-green-400"
    : result.viability.score >= 35
    ? "text-yellow-400"
    : "text-red-400";

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#020617] to-[#03162a] text-white px-6 py-10">
      <div className="max-w-5xl mx-auto space-y-8">

        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => router.push("/")}
            className="text-white/50 hover:text-white text-sm transition"
          >
            ← Back
          </button>
          <span className="text-xs text-white/30">
            Powered by FAISS + XGBoost + Llama 3
          </span>
        </div>

        {/* Title */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            {result.idea_info.cleaned_idea}
          </h1>
          <div className="flex flex-wrap gap-2 mt-3">
            <span className="px-3 py-1 rounded-full bg-cyan-400/10 border border-cyan-400/20 text-cyan-300 text-xs">
              {result.idea_info.market_category}
            </span>
            {result.idea_info.keywords.map((kw, i) => (
              <span key={i} className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs">
                {kw}
              </span>
            ))}
          </div>
        </div>

        {/* Top stats row */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white/5 border border-white/10 rounded-xl p-5 text-center">
            <p className="text-xs text-white/40 mb-1">Viability score</p>
            <p className={`text-4xl font-bold ${scoreColor}`}>
              {result.viability.score}
              <span className="text-lg text-white/30">/100</span>
            </p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl p-5 text-center">
            <p className="text-xs text-white/40 mb-1">Market crowding</p>
            <p className={`text-3xl font-bold ${crowdingColor}`}>
              {result.gap_analysis.crowding_level}
            </p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl p-5 text-center">
            <p className="text-xs text-white/40 mb-1">Gaps found</p>
            <p className="text-4xl font-bold text-purple-400">
              {result.gap_analysis.gaps.length}
            </p>
          </div>
        </div>

        {/* Idea info */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
          <h2 className="text-cyan-400 font-semibold">Idea breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-white/40 mb-1">Problem being solved</p>
              <p className="text-sm text-white/80">{result.idea_info.problem_being_solved}</p>
            </div>
            <div>
              <p className="text-xs text-white/40 mb-1">Target audience</p>
              <p className="text-sm text-white/80">{result.idea_info.target_audience}</p>
            </div>
            <div className="md:col-span-2">
              <p className="text-xs text-white/40 mb-1">Core value proposition</p>
              <p className="text-sm text-white/80">{result.idea_info.core_value_proposition}</p>
            </div>
          </div>
        </div>

        {/* Similar products */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-cyan-400 font-semibold mb-4">
            Similar products found
            <span className="text-white/30 text-xs ml-2">via FAISS semantic search</span>
          </h2>
          <div className="space-y-3">
            {result.similar_products.map((p, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-white/3 border border-white/5">
                <div>
                  <p className="text-sm font-medium text-white">{p.name}</p>
                  <p className="text-xs text-white/40">{p.tagline}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-white/30">similarity</p>
                  <p className="text-sm font-semibold text-cyan-300">
                    {(p.similarity * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gap analysis */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h2 className="text-cyan-400 font-semibold mb-4">Market gaps</h2>
            <div className="flex flex-wrap gap-2">
              {result.gap_analysis.gaps.slice(0, 6).map((gap, i) => (
                <span key={i} className="px-3 py-1 rounded-full bg-purple-400/10 border border-purple-400/20 text-purple-300 text-xs">
                  {gap}
                </span>
              ))}
            </div>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h2 className="text-cyan-400 font-semibold mb-4">Opportunities</h2>
            <div className="space-y-2">
              {result.gap_analysis.opportunities.map((opp, i) => (
                <p key={i} className="text-xs text-white/70 flex gap-2">
                  <span className="text-green-400 flex-shrink-0">→</span>
                  {opp}
                </p>
              ))}
            </div>
          </div>
        </div>

        {/* Viability score breakdown */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-cyan-400 font-semibold mb-4">
            Score breakdown
            <span className="text-white/30 text-xs ml-2">via SHAP explainability</span>
          </h2>
          <div className="space-y-3">
            {result.viability.shap_breakdown.map((item, i) => {
              const isPositive = item.value > 0;
              const barWidth = Math.min(100, Math.abs(item.value) * 1000);
              return (
                <div key={i} className="flex items-center gap-3">
                  <p className="text-xs text-white/50 w-40 flex-shrink-0">
                    {item.feature.replace(/_/g, " ")}
                  </p>
                  <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${isPositive ? "bg-green-400" : "bg-red-400"}`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                  <p className={`text-xs font-mono w-16 text-right ${isPositive ? "text-green-400" : "text-red-400"}`}>
                    {isPositive ? "+" : ""}{item.value.toFixed(3)}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* LLM Report */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-cyan-400 font-semibold mb-4">
            Full analysis report
            <span className="text-white/30 text-xs ml-2">generated by Llama 3</span>
          </h2>
          <div className="prose prose-invert prose-sm max-w-none">
            {result.report.split("\n").map((line, i) => {
              if (line.startsWith("**") && line.endsWith("**")) {
                return (
                  <p key={i} className="text-white font-semibold mt-4 mb-2">
                    {line.replace(/\*\*/g, "")}
                  </p>
                );
              }
              if (line.startsWith("* ") || line.startsWith("• ")) {
                return (
                  <p key={i} className="text-white/70 text-sm pl-4 flex gap-2">
                    <span className="text-cyan-400">•</span>
                    {line.replace(/^\*\s/, "").replace(/^•\s/, "")}
                  </p>
                );
              }
              if (line.trim() === "") return <br key={i} />;
              return (
                <p key={i} className="text-white/70 text-sm leading-relaxed">
                  {line}
                </p>
              );
            })}
          </div>
        </div>

      </div>
    </main>
  );
}