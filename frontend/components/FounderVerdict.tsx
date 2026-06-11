type Props = {
  competition: number;
  differentiation: number;
  opportunity: number;
};

export default function FounderVerdict({
  competition,
  differentiation,
  opportunity
}: Props) {

  let stars = 3;

  if (opportunity > 70 && differentiation > 40) {
    stars = 5;
  } else if (opportunity > 60) {
    stars = 4;
  }

  let verdict =
    "This market has room for a well-differentiated entrant. Focus on a narrow niche and a strong value proposition to carve out space.";

  if (competition > 80) {
    verdict =
      "This is a highly competitive market. Differentiation will be the deciding factor — a me-too product will not survive.";
  }

  if (differentiation > 60) {
    verdict =
      "Strong differentiation potential detected. A compelling unique angle can capture meaningful market share even against established players.";
  }

  let label = "Find Your Niche";
  let badgeColor = "bg-violet-500/10 text-violet-300 border-violet-500/20";

  if (opportunity > 70 && competition < 70) {
    label = "Strong Opportunity";
    badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  }

  if (competition > 85 && differentiation < 30) {
    label = "Highly Competitive";
    badgeColor = "bg-rose-500/10 text-rose-400 border-rose-500/20";
  }

  return (
    <div className="bg-gradient-to-br from-violet-950/40 to-indigo-950/20 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-violet-300 font-semibold">
          Founder Verdict
        </h2>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${badgeColor}`}>
          {label}
        </span>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <div className="text-2xl tracking-widest">
          {"★".repeat(stars)}
          <span className="text-white/15">{"★".repeat(5 - stars)}</span>
        </div>
        <span className="text-sm text-white/40">({stars}/5)</span>
      </div>

      <p className="text-white/75 leading-relaxed text-base">
        {verdict}
      </p>
    </div>
  );
}