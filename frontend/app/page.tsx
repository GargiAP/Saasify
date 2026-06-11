'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [idea, setIdea] = useState('');
  const router = useRouter();

  const handleSubmit = () => {
    if (!idea.trim()) return;
    router.push(`/analyze?idea=${encodeURIComponent(idea)}`);
  };

  const features = [
    { icon: "⚔️", label: "Competition Score", desc: "How saturated is your market" },
    { icon: "🎯", label: "Differentiation", desc: "How unique your angle is" },
    { icon: "🚀", label: "Opportunity Score", desc: "Overall market potential" },
    { icon: "🏢", label: "Top Competitors", desc: "Who you'll be up against" },
    { icon: "🗺️", label: "Market Gaps", desc: "Where incumbents fall short" },
    { icon: "📋", label: "Next Steps", desc: "What to build and prioritize" },
  ];

  return (
    <main className="min-h-screen bg-[#09090f] text-white flex flex-col">

      {/* Subtle top glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-violet-600/10 blur-[100px] pointer-events-none" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          <div className="h-7 w-7 rounded-lg bg-violet-600 flex items-center justify-center text-white text-xs font-bold">✦</div>
          <span className="font-semibold text-white">Saasify</span>
        </div>
        <span className="text-xs text-white/30 tracking-widest uppercase hidden sm:block">Startup Intelligence</span>
      </nav>

      {/* Hero */}
      <section className="relative z-10 flex flex-col items-center text-center px-6 pt-24 pb-16">

        <div className="inline-flex items-center gap-2 bg-violet-500/10 rounded-full px-4 py-1.5 mb-8">
          <span className="h-1.5 w-1.5 rounded-full bg-violet-400 animate-pulse" />
          <span className="text-xs text-violet-300 font-medium">Research before you build</span>
        </div>

        <h1 className="max-w-3xl text-5xl md:text-6xl font-bold leading-tight text-white">
          Turn your idea into <br />
          <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            market clarity
          </span>
        </h1>

        <p className="mt-5 max-w-lg text-[15px] text-white/50 leading-relaxed">
          Get an instant, founder-focused market intelligence report. Understand your competition, find your gaps, and know exactly what to build first.
        </p>

        {/* Input box */}
        <div className="mt-10 w-full max-w-2xl">
          <div className="flex gap-2 bg-white/[0.06] rounded-xl p-1.5">
            <input
              type="text"
              placeholder="e.g. AI tool that helps solo founders write cold emails..."
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleSubmit(); }}
              className="flex-1 bg-transparent px-4 py-3 text-sm text-white placeholder:text-white/30 outline-none"
            />
            <button
              onClick={handleSubmit}
              disabled={!idea.trim()}
              className="shrink-0 bg-violet-600 hover:bg-violet-500 disabled:opacity-30 disabled:cursor-not-allowed text-white text-sm font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              Analyze →
            </button>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-3 gap-3 max-w-2xl w-full">
          {features.map((f) => (
            <div key={f.label} className="bg-white/[0.04] rounded-xl p-4 text-left">
              <div className="text-xl mb-2">{f.icon}</div>
              <p className="text-sm font-medium text-white/90">{f.label}</p>
              <p className="text-xs text-white/40 mt-0.5">{f.desc}</p>
            </div>
          ))}
        </div>

      </section>
    </main>
  );
}