export default function OpportunityGauge({
  score
}: {
  score: number;
}) {

  const width = Math.min(
    Math.max(score, 0),
    100
  );

  return (

    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">

      <h2 className="text-cyan-400 font-semibold mb-4">
        Opportunity Potential
      </h2>

      <div className="w-full h-4 bg-white/10 rounded-full overflow-hidden">

        <div
          className="
          h-full
          bg-gradient-to-r
          from-red-500
          via-yellow-500
          to-green-500
          "
          style={{
            width: `${width}%`
          }}
        />

      </div>

      <div className="mt-4 flex items-center justify-between">

        <span className="text-white/40">
          Low
        </span>

        <span className="text-4xl font-bold text-green-400">
          {score}
        </span>

        <span className="text-white/40">
          High
        </span>

      </div>

    </div>
  );
}