type SWOTProps = {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
};

export default function SWOTAnalysis({
  strengths,
  weaknesses,
  opportunities,
  threats,
}: SWOTProps) {
  const showThreats = threats && threats.length > 0;

  return (
    <div className="bg-white/4 rounded-2xl p-6">
      <h2 className="text-white/90 font-semibold mb-6">
        Market Gaps & Opportunities to Exploit
      </h2>

      <div className="grid md:grid-cols-2 gap-5">

        {/* Strengths */}
        <div className="rounded-xl bg-emerald-500/5 p-5 transition-all duration-300">
          <div className="flex items-center gap-2 mb-3">
            <div className="h-2 w-2 rounded-full bg-emerald-400" />
            <h3 className="text-sm font-semibold text-emerald-300">
              Core Strengths
            </h3>
          </div>
          <ul className="space-y-2">
            {strengths.map((item, index) => (
              <li key={index} className="text-sm text-white/55 flex items-start gap-2">
                <span className="text-emerald-400/60 select-none mt-0.5">›</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Product Gaps / Missing Features */}
        <div className="rounded-xl bg-violet-500/5 p-5 transition-all duration-300">
          <div className="flex items-center gap-2 mb-3">
            <div className="h-2 w-2 rounded-full bg-violet-400" />
            <h3 className="text-sm font-semibold text-violet-300">
              Market & Product Gaps
            </h3>
          </div>
          <ul className="space-y-2">
            {opportunities.map((item, index) => (
              <li key={index} className="text-sm text-white/55 flex items-start gap-2">
                <span className="text-violet-400/60 select-none mt-0.5">›</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Internal Risks */}
        <div className="rounded-xl bg-rose-500/5 p-5 transition-all duration-300">
          <div className="flex items-center gap-2 mb-3">
            <div className="h-2 w-2 rounded-full bg-rose-400" />
            <h3 className="text-sm font-semibold text-rose-300">
              Internal Risks
            </h3>
          </div>
          <ul className="space-y-2">
            {weaknesses.map((item, index) => (
              <li key={index} className="text-sm text-white/55 flex items-start gap-2">
                <span className="text-rose-400/60 select-none mt-0.5">›</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Macro Threats */}
        {showThreats && (
          <div className="rounded-xl bg-amber-500/5 p-5 transition-all duration-300">
            <div className="flex items-center gap-2 mb-3">
              <div className="h-2 w-2 rounded-full bg-amber-400" />
              <h3 className="text-sm font-semibold text-amber-300">
                Macro Market Threats
              </h3>
            </div>
            <ul className="space-y-2">
              {threats.map((item, index) => (
                <li key={index} className="text-sm text-white/55 flex items-start gap-2">
                  <span className="text-amber-400/60 select-none mt-0.5">›</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}