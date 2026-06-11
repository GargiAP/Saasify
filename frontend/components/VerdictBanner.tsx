type Props = {
  competition: number
  differentiation: number
  opportunity: number
}

export default function VerdictBanner({
  competition,
  differentiation,
  opportunity
}: Props) {

  let verdict = "Proceed with Caution";
  let color = "text-yellow-400";

  if (
    opportunity > 70 &&
    competition < 70
  ) {
    verdict = "Strong Opportunity";
    color = "text-green-400";
  }

  if (
    competition > 85 &&
    differentiation < 30
  ) {
    verdict = "Highly Competitive";
    color = "text-red-400";
  }

  return (

    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">

      <p className="text-sm text-white/50 mb-2">
        Final Recommendation
      </p>

      <h2 className={`text-3xl font-bold ${color}`}>
        {verdict}
      </h2>

      <p className="text-white/70 mt-3">
        Opportunity Score: {opportunity}
        {" • "}
        Competition: {competition}
        {" • "}
        Differentiation: {differentiation}
      </p>

    </div>

  );
}