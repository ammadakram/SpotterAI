import type { PlannedRoute } from '../../lib/api'
import { formatDuration, formatMiles, formatTime } from '../../lib/format'
import { RISK_COLOURS } from '../../lib/risk'

type Props = {
  route: PlannedRoute
  isRecommended: boolean
  isSelected: boolean
  onSelect: () => void
}

export function RouteCard({ route, isRecommended, isSelected, onSelect }: Props) {
  return (
    <button
      type="button"
      aria-pressed={isSelected}
      onClick={onSelect}
      className={`w-full rounded-md border px-4 py-3 text-left text-sm ${
        isSelected
          ? 'border-blue-600 ring-1 ring-blue-600'
          : 'border-slate-200 hover:border-slate-400'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-slate-900">{route.label}</span>
        {isRecommended && (
          <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
            Recommended
          </span>
        )}
        {!route.isDrivable && (
          <span className="rounded bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-900">
            Not drivable
          </span>
        )}
      </div>
      <div className="mt-1 text-slate-600">
        {formatMiles(route.distanceMi)} · {formatDuration(route.durationS)} · arrives{' '}
        {formatTime(route.arrivalAt)}
      </div>

      <RiskStrip route={route} />

      {/* The numbers the ranking compares, always visible. */}
      <div className="mt-2 text-slate-600">{summary(route)}</div>
    </button>
  )
}

/** The route as a bar: each stretch drawn in its risk colour, where it happens. */
function RiskStrip({ route }: { route: PlannedRoute }) {
  return (
    <div className="mt-2 flex h-2 overflow-hidden rounded-full" aria-hidden>
      {route.stretches.map((stretch) => (
        <div
          key={stretch.fromMi}
          style={{
            width: `${((stretch.toMi - stretch.fromMi) / route.distanceMi) * 100}%`,
            backgroundColor: RISK_COLOURS[stretch.level],
          }}
        />
      ))}
    </div>
  )
}

/** "Severe 30 mi · High 0 mi · Avg 0.80"; No travel and No forecast only when present. */
function summary(route: PlannedRoute): string {
  const { noTravel, severe, high, unknown } = route.riskMiles
  const parts = [
    noTravel > 0 && `No travel ${formatMiles(noTravel)}`,
    `Severe ${formatMiles(severe)}`,
    `High ${formatMiles(high)}`,
    `Avg ${route.averageRisk.toFixed(2)}`,
    unknown > 0 && `No forecast ${formatMiles(unknown)}`,
  ]
  return parts.filter(Boolean).join(' · ')
}
