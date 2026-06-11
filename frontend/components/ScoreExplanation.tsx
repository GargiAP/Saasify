type Props = {
  competitors: number
  clusterSize: number
  competition: number
  differentiation: number
  opportunities: number
}

export default function ScoreExplanation({
  competitors,
  clusterSize,
  competition,
  differentiation,
  opportunities
}: Props) {

  return (

    <div className="grid md:grid-cols-3 gap-5">

      <div className="bg-white/5 border border-white/10 rounded-xl p-5">

        <h3 className="font-semibold mb-3">
          Competition Analysis
        </h3>

        <ul className="space-y-2 text-sm text-white/70">

          <li>
            • {clusterSize} startups in cluster
          </li>

          <li>
            • {competitors} competitors found
          </li>

          <li>
            • Competition score {competition}
          </li>

        </ul>

      </div>

      <div className="bg-white/5 border border-white/10 rounded-xl p-5">

        <h3 className="font-semibold mb-3">
          Differentiation Analysis
        </h3>

        <ul className="space-y-2 text-sm text-white/70">

          <li>
            • Differentiation score {differentiation}
          </li>

          <li>
            • Similar customer groups exist
          </li>

          <li>
            • Similar solutions detected
          </li>

        </ul>

      </div>

      <div className="bg-white/5 border border-white/10 rounded-xl p-5">

        <h3 className="font-semibold mb-3">
          Opportunity Analysis
        </h3>

        <ul className="space-y-2 text-sm text-white/70">

          <li>
            • {opportunities} market gaps found
          </li>

          <li>
            • Expansion opportunities exist
          </li>

          <li>
            • Opportunity score {Math.round(opportunities)}
          </li>

        </ul>

      </div>

    </div>

  );
}