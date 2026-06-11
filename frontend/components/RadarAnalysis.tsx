'use client';

import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer
} from 'recharts';

export default function RadarAnalysis({
  competition,
  differentiation,
  opportunity
}: {
  competition: number;
  differentiation: number;
  opportunity: number;
}) {

  const data = [
    {
      metric: "Competition",
      value: competition
    },
    {
      metric: "Differentiation",
      value: differentiation
    },
    {
      metric: "Opportunity",
      value: opportunity
    }
  ];

  return (

    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 h-[380px]">

      <h2 className="text-cyan-400 font-semibold mb-4">
        Strategic Position
      </h2>

      <ResponsiveContainer
        width="100%"
        height="100%"
      >

        <RadarChart data={data}>

          <PolarGrid />

          <PolarAngleAxis
            dataKey="metric"
          />

          <PolarRadiusAxis />

          <Radar
            dataKey="value"
            stroke="#22d3ee"
            fill="#22d3ee"
            fillOpacity={0.35}
          />

        </RadarChart>

      </ResponsiveContainer>

    </div>
  );
}