import type { Plan } from '../../lib/api'
import { RouteCard } from './RouteCard'

type Props = {
  plan: Plan
  selectedRouteId: string | null
  onSelect: (routeId: string) => void
}

/** Drivable routes in ranked order, then the ones with No Travel. */
export function RouteList({ plan, selectedRouteId, onSelect }: Props) {
  const rankIndex = new Map(plan.ranking.orderedRouteIds.map((id, index) => [id, index]))
  const routes = [...plan.routes].sort(
    (a, b) => (rankIndex.get(a.id) ?? Infinity) - (rankIndex.get(b.id) ?? Infinity),
  )
  return (
    <ul className="space-y-2">
      {routes.map((route) => (
        <li key={route.id}>
          <RouteCard
            route={route}
            isRecommended={route.id === plan.ranking.recommendedRouteId}
            isSelected={route.id === selectedRouteId}
            onSelect={() => onSelect(route.id)}
          />
        </li>
      ))}
    </ul>
  )
}
