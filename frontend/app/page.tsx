'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {

  const [idea, setIdea] = useState('');
  const router = useRouter();

  const handleSubmit = () => {

    console.log("Analyze clicked");

    if (!idea.trim()) {
      alert('Please describe your idea');
      return;
    }

    const encodedIdea = encodeURIComponent(idea);

    router.push(`/analyze?idea=${encodedIdea}`);
  };

  return (
    <main className="relative min-h-screen bg-gradient-to-br from-[#020617] via-[#020617] to-[#03162a] text-white overflow-hidden">

      {/* Glow background */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/20 blur-[160px]" />
      </div>

      {/* Navbar */}
      <nav className="flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">

        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-cyan-400 flex items-center justify-center font-bold text-black">
            ✦
          </div>
          <span className="text-lg font-semibold">Saasify</span>
        </div>

        <span className="text-sm text-white/50">
          v1.0 — Research & Validation
        </span>

      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-6 mt-24">

        <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-1 text-sm text-cyan-300">
          ✨ Research before you build
        </span>

        <h1 className="max-w-4xl text-4xl md:text-6xl font-bold leading-tight">
          Turn your idea into <br />
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            market clarity
          </span>
        </h1>

        <p className="mt-6 max-w-2xl text-white/60">
          Enter your SaaS idea and get clarity on target users, assumptions,
          competition, gaps, and viability.
        </p>

        {/* Input */}
        <div className="mt-10 flex w-full max-w-2xl items-center gap-3 rounded-xl bg-white/5 p-3 backdrop-blur border border-white/10">

          <input
            type="text"
            placeholder="Describe your SaaS idea..."
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSubmit();
            }}
            className="flex-1 bg-transparent px-3 py-3 text-sm outline-none placeholder:text-white/40"
          />

          <button
            type="button"
            onClick={handleSubmit}
            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-400 to-blue-500 px-6 py-3 text-sm font-semibold text-black hover:opacity-90 transition"
          >
            Analyze →
          </button>

        </div>

      </section>
    </main>
  );
}