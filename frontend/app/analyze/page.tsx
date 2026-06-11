'use client';

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { analyzeIdea } from "@/services/mlService";
import { AnalysisResult } from "@/types/analysis";

function Section({ label, color, children }: { label: string; color: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <div className={`h-5 w-1 rounded-full ${color}`} />
        <h2 className="text-sm font-semibold text-white/50 uppercase tracking-widest">{label}</h2>
      </div>
      {children}
    </div>
  );
}

function AnalyzePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const idea = searchParams.get("idea");
  const reportRef = useRef<HTMLDivElement>(null);

  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!idea) return;
    const run = async () => {
      try {
        const data = await analyzeIdea(idea);
        setResult(data);
      } catch {
        setError("Analysis failed. Make sure the ML service is running.");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [idea]);

  const handleDownloadPDF = async () => {
    if (!reportRef.current) return;
    setDownloading(true);
    try {
      const html2pdf = (await import("html2pdf.js")).default;
      const ideaSlug = result?.idea?.slice(0, 40).replace(/\s+/g, "-").toLowerCase() ?? "report";
      await html2pdf()
        .set({
          margin: [10, 10, 10, 10],
          filename: `saasify-report-${ideaSlug}.pdf`,
          image: { type: "jpeg", quality: 0.97 },
          html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: "#09090f",
          },
          jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
        })
        .from(reportRef.current)
        .save();
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090f] text-white flex flex-col items-center justify-center gap-5">
        <div className="h-9 w-9 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
        <div className="text-center">
          <p className="text-white text-sm font-medium">Running Startup Intelligence Engine</p>
          <p className="text-white/40 text-xs mt-1">Analyzing competition, gaps, and opportunities...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#09090f] text-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-red-400 text-sm">{error}</p>
          <button onClick={() => router.push("/")} className="text-violet-400 hover:text-violet-300 text-sm transition-colors">
            ← Go back
          </button>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const compLevel = result.market_intelligence.competition.level;
  const compScore = result.market_intelligence.competition.score;
  const diffScore = result.market_intelligence.differentiation_score;
  const oppScore = result.market_intelligence.opportunity_score;

  let verdictLabel = "Find Your Niche";
  let verdictColor = "text-amber-400";
  let verdictBg = "bg-amber-500/10";
  let verdictText = "This market has room for a well-differentiated entrant. Focus on a narrow niche and a strong value proposition.";
  let stars = 3;

  if (oppScore > 70 && compScore < 70) {
    verdictLabel = "Strong Opportunity";
    verdictColor = "text-emerald-400";
    verdictBg = "bg-emerald-500/10";
    verdictText = "The market signals are favourable. Low competition and strong opportunity make this worth pursuing — move fast.";
    stars = oppScore > 80 ? 5 : 4;
  } else if (compScore > 85 && diffScore < 30) {
    verdictLabel = "Highly Competitive";
    verdictColor = "text-red-400";
    verdictBg = "bg-red-500/10";
    verdictText = "This is a crowded space. A me-too product will not survive. Differentiation is non-negotiable to get traction.";
    stars = 2;
  } else if (diffScore > 60) {
    verdictLabel = "Strong Differentiation";
    verdictColor = "text-violet-400";
    verdictBg = "bg-violet-500/10";
    verdictText = "Strong differentiation potential detected. A compelling unique angle can capture meaningful market share.";
    stars = 4;
  }

  const gaps = result.market_gap;
  const recs = result.recommendations;

  return (
    <main className="min-h-screen bg-[#09090f] text-white">
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[500px] h-[250px] bg-violet-600/8 blur-[100px] pointer-events-none" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-4 border-b border-white/[0.06]">
        <button onClick={() => router.push("/")} className="flex items-center gap-2 text-white/40 hover:text-white text-sm transition-colors">
          <span>←</span>
          <span className="flex items-center gap-1.5">
            <div className="h-5 w-5 rounded bg-violet-600 flex items-center justify-center text-white text-[10px] font-bold">✦</div>
            <span className="font-medium text-white/70">Saasify</span>
          </span>
        </button>

        <button
          onClick={handleDownloadPDF}
          disabled={downloading}
          className="flex items-center gap-2 bg-white/[0.07] hover:bg-white/[0.11] disabled:opacity-50 disabled:cursor-not-allowed text-white/80 hover:text-white text-sm font-medium px-4 py-2 rounded-lg transition-all"
        >
          {downloading ? (
            <>
              <div className="h-3.5 w-3.5 border border-white/40 border-t-white/80 rounded-full animate-spin" />
              <span>Generating PDF...</span>
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M8 12l4 4m0 0l4-4m-4 4V4" />
              </svg>
              <span>Download PDF</span>
            </>
          )}
        </button>
      </nav>

      {/* Report content — wrapped in ref for PDF capture */}
      <div ref={reportRef} className="relative z-10 max-w-4xl mx-auto px-6 py-10 space-y-12" style={{ backgroundColor: "#09090f" }}>

        {/* Idea Header */}
        <div>
          <p className="text-xs text-white/30 uppercase tracking-widest mb-3">Saasify · Startup Intelligence Report</p>
          <h1 className="text-2xl font-semibold text-white leading-snug">"{result.idea}"</h1>
          <div className="flex flex-wrap gap-2 mt-4">
            <span className="bg-violet-600/20 text-violet-300 text-xs font-medium px-3 py-1 rounded-full">
              {result.market_intelligence.market_segment}
            </span>
            {result.idea_meta.industry && (
              <span className="bg-white/[0.06] text-white/60 text-xs px-3 py-1 rounded-full">
                {result.idea_meta.industry}
              </span>
            )}
            {result.idea_meta.subcategory && (
              <span className="bg-white/[0.06] text-white/60 text-xs px-3 py-1 rounded-full">
                {result.idea_meta.subcategory}
              </span>
            )}
          </div>
        </div>

        {/* ── SECTION 1: CORE METRICS ── */}
        <Section label="Core Metrics" color="bg-violet-500">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#111119] rounded-2xl p-5">
              <p className="text-xs text-white/40 mb-4">Competition</p>
              <p className={`text-5xl font-bold mb-2 ${
                compLevel === 'High' ? 'text-red-400' :
                compLevel === 'Medium' ? 'text-amber-400' : 'text-emerald-400'
              }`}>{compScore}</p>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                compLevel === 'High' ? 'bg-red-500/15 text-red-400' :
                compLevel === 'Medium' ? 'bg-amber-500/15 text-amber-400' : 'bg-emerald-500/15 text-emerald-400'
              }`}>{compLevel} Saturation</span>
            </div>
            <div className="bg-[#111119] rounded-2xl p-5">
              <p className="text-xs text-white/40 mb-4">Differentiation</p>
              <p className="text-5xl font-bold text-violet-400 mb-2">{diffScore}</p>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-violet-500/15 text-violet-400">
                {diffScore > 60 ? 'Strong' : 'Moderate'}
              </span>
            </div>
            <div className="bg-[#111119] rounded-2xl p-5">
              <p className="text-xs text-white/40 mb-4">Opportunity</p>
              <p className="text-5xl font-bold text-emerald-400 mb-2">{oppScore}</p>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-400">
                {oppScore > 70 ? 'High' : 'Moderate'}
              </span>
            </div>
          </div>
        </Section>

        {/* ── SECTION 2: VERDICT ── */}
        <Section label="Final Verdict" color="bg-amber-500">
          <div className="bg-[#111119] rounded-2xl p-6">
            <div className={`inline-flex items-center gap-2 ${verdictBg} rounded-full px-4 py-1.5 mb-4`}>
              <span className={`text-sm font-bold ${verdictColor}`}>{verdictLabel}</span>
            </div>
            <div className="flex gap-0.5 mb-4 text-xl">
              {Array.from({ length: 5 }).map((_, i) => (
                <span key={i} className={i < stars ? 'text-amber-400' : 'text-white/15'}>★</span>
              ))}
              <span className="text-white/30 text-sm ml-2 self-center">{stars}/5</span>
            </div>
            <p className="text-white/75 text-[15px] leading-relaxed max-w-xl">{verdictText}</p>
          </div>
        </Section>

        {/* ── SECTION 3: TOP COMPETITORS ── */}
        <Section label="Top Competitors" color="bg-red-500">
          <div className="bg-[#111119] rounded-2xl overflow-hidden">
            {result.competitors.slice(0, 3).map((competitor, i) => (
              <div key={i} className={`flex items-center gap-4 px-6 py-4 ${i < 2 ? 'border-b border-white/[0.06]' : ''}`}>
                <span className="text-xs text-white/20 font-mono w-4 shrink-0">{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-semibold text-white">{competitor.name}</span>
                    {competitor.reasons?.slice(0, 2).map((r, idx) => (
                      <span key={idx} className="text-[11px] bg-white/[0.06] text-white/50 px-2 py-0.5 rounded-full">{r}</span>
                    ))}
                  </div>
                  {competitor.solution && (
                    <p className="text-xs text-white/40 mt-1 truncate">{competitor.solution}</p>
                  )}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <div className="w-20 h-1.5 bg-white/10 rounded-full overflow-hidden hidden sm:block">
                    <div className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full" style={{ width: `${competitor.score}%` }} />
                  </div>
                  <span className="text-sm font-semibold text-white/70 w-10 text-right">{Math.round(competitor.score)}%</span>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* ── SECTION 4: MARKET GAPS ── */}
        <Section label="Market Gaps & Opportunities" color="bg-emerald-500">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-[#111119] rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <div className="h-6 w-6 rounded-lg bg-emerald-500/15 flex items-center justify-center">
                  <span className="text-emerald-400 text-xs font-bold">↑</span>
                </div>
                <h3 className="text-sm font-semibold text-emerald-400">Core Strengths</h3>
              </div>
              <ul className="space-y-2.5">
                {gaps.opportunities.map((item, i) => (
                  <li key={i} className="text-sm text-white/70 flex gap-2.5">
                    <span className="text-emerald-500/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-[#111119] rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <div className="h-6 w-6 rounded-lg bg-violet-500/15 flex items-center justify-center">
                  <span className="text-violet-400 text-xs font-bold">◇</span>
                </div>
                <h3 className="text-sm font-semibold text-violet-400">Product Gaps</h3>
              </div>
              <ul className="space-y-2.5">
                {gaps.missing_features.map((item, i) => (
                  <li key={i} className="text-sm text-white/70 flex gap-2.5">
                    <span className="text-violet-500/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-[#111119] rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <div className="h-6 w-6 rounded-lg bg-red-500/15 flex items-center justify-center">
                  <span className="text-red-400 text-xs font-bold">!</span>
                </div>
                <h3 className="text-sm font-semibold text-red-400">Internal Risks</h3>
              </div>
              <ul className="space-y-2.5">
                {gaps.risks.map((item, i) => (
                  <li key={i} className="text-sm text-white/70 flex gap-2.5">
                    <span className="text-red-500/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {gaps.threats && gaps.threats.length > 0 && (
              <div className="bg-[#111119] rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-4">
                  <div className="h-6 w-6 rounded-lg bg-amber-500/15 flex items-center justify-center">
                    <span className="text-amber-400 text-xs font-bold">⚡</span>
                  </div>
                  <h3 className="text-sm font-semibold text-amber-400">Market Threats</h3>
                </div>
                <ul className="space-y-2.5">
                  {gaps.threats.map((item, i) => (
                    <li key={i} className="text-sm text-white/70 flex gap-2.5">
                      <span className="text-amber-500/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Section>

        {/* ── SECTION 5: NEXT STEPS ── */}
        <Section label="Recommended Next Steps" color="bg-indigo-500">
          <div className="bg-[#111119] rounded-2xl divide-y divide-white/[0.06]">
            {recs.feature_suggestions?.length > 0 && (
              <div className="p-6">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <span className="h-5 w-5 rounded-md bg-violet-600/30 flex items-center justify-center text-violet-400 text-[11px] font-bold">1</span>
                  Features to Build First
                </h3>
                <ul className="space-y-2">
                  {recs.feature_suggestions.map((item, i) => (
                    <li key={i} className="text-sm text-white/65 flex gap-2.5">
                      <span className="text-violet-400/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {recs.positioning?.length > 0 && (
              <div className="p-6">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <span className="h-5 w-5 rounded-md bg-indigo-600/30 flex items-center justify-center text-indigo-400 text-[11px] font-bold">2</span>
                  Positioning Strategy
                </h3>
                <ul className="space-y-2">
                  {recs.positioning.map((item, i) => (
                    <li key={i} className="text-sm text-white/65 flex gap-2.5">
                      <span className="text-indigo-400/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {recs.monetization?.length > 0 && (
              <div className="p-6">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <span className="h-5 w-5 rounded-md bg-emerald-600/30 flex items-center justify-center text-emerald-400 text-[11px] font-bold">3</span>
                  Monetization Models
                </h3>
                <ul className="space-y-2">
                  {recs.monetization.map((item, i) => (
                    <li key={i} className="text-sm text-white/65 flex gap-2.5">
                      <span className="text-emerald-400/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {recs.customer_segments?.length > 0 && (
              <div className="p-6">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                  <span className="h-5 w-5 rounded-md bg-amber-600/30 flex items-center justify-center text-amber-400 text-[11px] font-bold">4</span>
                  Customer Segments to Target
                </h3>
                <ul className="space-y-2">
                  {recs.customer_segments.map((item, i) => (
                    <li key={i} className="text-sm text-white/65 flex gap-2.5">
                      <span className="text-amber-400/60 shrink-0 mt-0.5">›</span><span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Section>

        {/* PDF Footer */}
        <div className="border-t border-white/[0.06] pt-6 flex items-center justify-between">
          <span className="text-xs text-white/20">Generated by Saasify · Startup Intelligence</span>
          <span className="text-xs text-white/20">{new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
        </div>

      </div>
    </main>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#09090f] text-white flex items-center justify-center">
        <div className="h-8 w-8 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
      </div>
    }>
      <AnalyzePageContent />
    </Suspense>
  );
}