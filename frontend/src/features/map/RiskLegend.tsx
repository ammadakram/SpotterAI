import { HEATMAP_STEPS, VARIABLE_LABELS, type HeatmapVariable } from '../../lib/heatmap'
import { RISK_COLOURS } from '../../lib/risk'

/** Colours of the corridor heatmap for the chosen variable. Checkpoint dots always show risk. */
export function RiskLegend({ variable }: { variable: HeatmapVariable }) {
  return (
    <div className="absolute bottom-8 left-2 rounded-md bg-white/90 px-3 py-2 text-xs text-slate-700 shadow">
      <div className="mb-1 font-medium">{VARIABLE_LABELS[variable]}</div>
      <ul className="space-y-0.5">
        {HEATMAP_STEPS[variable].map((step) => (
          <li key={step.label} className="flex items-center gap-2">
            <Swatch colour={step.colour} />
            {step.label}
          </li>
        ))}
        <li className="flex items-center gap-2">
          <Swatch colour={RISK_COLOURS.NO_FORECAST} />
          No forecast
        </li>
      </ul>
      {variable !== 'risk' && (
        <div className="mt-1 max-w-36 text-slate-500">Dots: risk at the truck's ETA</div>
      )}
    </div>
  )
}

function Swatch({ colour }: { colour: string }) {
  return <span className="inline-block size-2.5 rounded-sm" style={{ backgroundColor: colour }} />
}
