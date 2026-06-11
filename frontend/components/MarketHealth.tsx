type Props = {
  competition: number
  differentiation: number
  opportunity: number
}

export default function MarketHealth({
  competition,
  differentiation,
  opportunity
}: Props) {

  const score = Math.round(

    (
      opportunity
      +
      differentiation
      +
      (100 - competition)
    ) / 3

  );

  const label =
    score > 70
      ? "Healthy Market"
      : score > 50
      ? "Moderately Healthy"
      : "Difficult Market";

  return (

    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">

      <h2 className="text-cyan-400 font-semibold mb-4">
        Market Health
      </h2>

      <div className="text-6xl font-bold text-green-400">
        {score}
      </div>

      <p className="text-white/60 mt-3">
        {label}
      </p>

    </div>

  );
}