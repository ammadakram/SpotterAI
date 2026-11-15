import { RISK_COLOURS, RISK_LABELS, RISK_LEVELS } from '../../lib/risk'

export function RiskLegend() {
  return (
    <ul className="absolute bottom-8 left-2 space-y-0.5 rounded-md bg-white/90 px-3 py-2 text-xs text-slate-700 shadow">
      {RISK_LEVELS.map((level) => (
        <li key={level} className="flex items-center gap-2">
          <span
            className="inline-block size-2.5 rounded-full"
            style={{ backgroundColor: RISK_COLOURS[level] }}
          />
          {RISK_LABELS[level]}
        </li>
      ))}
    </ul>
  )
}
