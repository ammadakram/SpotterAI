import type { PlannedRoute } from '../../lib/api'
import { formatDuration, formatMiles, formatTime } from '../../lib/format'

type Props = {
  routes: PlannedRoute[]
  selectedRouteId: string | null
  onSelect: (routeId: string) => void
}

export function RouteList({ routes, selectedRouteId, onSelect }: Props) {
  return (
    <ul className="space-y-2">
      {routes.map((route) => {
        const isSelected = route.id === selectedRouteId
        return (
          <li key={route.id}>
            <button
              type="button"
              aria-pressed={isSelected}
              onClick={() => onSelect(route.id)}
              className={`w-full rounded-md border px-4 py-3 text-left text-sm ${
                isSelected
                  ? 'border-blue-600 ring-1 ring-blue-600'
                  : 'border-slate-200 hover:border-slate-400'
              }`}
            >
              <div className="font-medium text-slate-900">{route.label}</div>
              <div className="mt-1 text-slate-600">
                {formatMiles(route.distanceMi)} · {formatDuration(route.durationS)} · arrives{' '}
                {formatTime(route.arrivalAt)}
              </div>
              <div className="mt-1 text-slate-500">{route.checkpoints.length} checkpoints</div>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
