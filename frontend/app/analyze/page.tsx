'use client';

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

export default function AnalyzePage() {

  const router = useRouter();
  const searchParams = useSearchParams();

  const idea = searchParams.get("idea");

  const [loading, setLoading] = useState(true);
  const [interpretation, setInterpretation] = useState<any>(null);
  const [marketCategory, setMarketCategory] = useState<string | null>(null);
  const [similarityScore, setSimilarityScore] = useState<number | null>(null);

  useEffect(() => {

    if (!idea) return;

    const analyze = async () => {

      try {

        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ idea }),
        });

        const data = await res.json();

        if (data.success) {
          setInterpretation(data.interpretation);
          setMarketCategory(data.market_category);
          setSimilarityScore(data.similarity_score);
        }

      } catch (err) {
        console.error(err);
      }

      setLoading(false);

    };

    analyze();

  }, [idea]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] text-white flex items-center justify-center">
        Analyzing your idea...
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#020617] to-[#03162a] text-white px-6 py-10">

      <div className="max-w-5xl mx-auto space-y-8">

        {/* Back button */}

        <button
          onClick={() => router.push("/")}
          className="text-white/60 hover:text-white"
        >
          ← Back
        </button>


        {/* Page Title */}

        <h1 className="text-3xl font-bold">
          Analysis for:{" "}
          <span className="text-cyan-400">{idea}</span>
        </h1>


        {/* INTERPRETATION CARD */}

        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur">

          <h2 className="text-xl font-semibold mb-6 text-cyan-400">
            Idea Interpretation
          </h2>

          <div className="space-y-6">

            {/* Target User */}

            <div>
              <p className="text-sm text-white/40 mb-1">
                Target User
              </p>

              <p className="text-white/90">
                {interpretation?.target_user}
              </p>
            </div>


            {/* Problem */}

            <div>
              <p className="text-sm text-white/40 mb-1">
                Problem
              </p>

              <p className="text-white/90">
                {interpretation?.problem_statement}
              </p>
            </div>


            {/* Solution */}

            <div>
              <p className="text-sm text-white/40 mb-1">
                Solution
              </p>

              <p className="text-white/90">
                {interpretation?.solution_summary}
              </p>
            </div>

          </div>

        </div>


        {/* ML SERVICE CARD */}

        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur">

          <h2 className="text-xl font-semibold mb-6 text-cyan-400">
            ML Market Classification
          </h2>

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-white/40">
                Market Category
              </p>

              <p className="text-xl font-semibold text-cyan-300 mt-1">
                {marketCategory ?? "Unknown"}
              </p>

            </div>


            <div className="text-right">

              <p className="text-sm text-white/40">
                Similarity Score
              </p>

              <p className="text-xl font-semibold text-emerald-400 mt-1">
                {similarityScore
                  ? `${(similarityScore * 100).toFixed(1)}%`
                  : "—"}
              </p>

            </div>

          </div>

        </div>

      </div>

    </main>
  );
}