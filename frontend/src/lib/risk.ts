import type { PlannedRoute, Plan, RiskLevel, RiskMiles } from './api'
import { formatDuration } from './format'

export const RISK_LEVELS: RiskLevel[] = [
  'LOW',
  'MODERATE',
  'HIGH',
  'SEVERE',
  'NO_TRAVEL',
  'NO_FORECAST',
]

export const RISK_LABELS: Record<RiskLevel, string> = {
  LOW: 'Low',
  MODERATE: 'Moderate',
  HIGH: 'High',
  SEVERE: 'Severe',
  NO_TRAVEL: 'No travel',
  NO_FORECAST: 'No forecast',
}

export const RISK_COLOURS: Record<RiskLevel, string> = {
  LOW: '#16a34a',
  MODERATE: '#eab308',
  HIGH: '#f97316',
  SEVERE: '#dc2626',
  NO_TRAVEL: '#581c87',
  NO_FORECAST: '#94a3b8',
}

/** One sentence on why the recommended route won, comparing it with the runner-up. */
export function recommendationReason(plan: Plan): string | null {
  const { orderedRouteIds, decidedBy } = plan.ranking
  const byId = new Map(plan.routes.map((route) => [route.id, route]))
  const best = byId.get(orderedRouteIds[0])
  const next = byId.get(orderedRouteIds[1])
  if (!best || !decidedBy) return null
  if (decidedBy === 'ONLY_DRIVABLE') return 'The only route without No Travel conditions.'
  if (!next) return null

  const vs = (a: string, b: string) => `${a} vs ${b} on ${next.label}`
  switch (decidedBy) {
    case 'SEVERE_MILES':
      return `Fewest Severe miles: ${vs(miles(best, 'severe'), miles(next, 'severe'))}.`
    case 'HIGH_MILES':
      return `Same Severe miles, fewer High miles: ${vs(miles(best, 'high'), miles(next, 'high'))}.`
    case 'AVERAGE_RISK':
      return `Same Severe and High miles, lower average risk: ${vs(
        best.averageRisk.toFixed(2),
        next.averageRisk.toFixed(2),
      )}.`
    case 'DURATION':
      // A full tie also reports DURATION; the backend then keeps HERE's order.
      if (Math.round(best.durationS) === Math.round(next.durationS))
        return 'Equal on risk and travel time; listed first by the routing service.'
      return `Equal risk, shorter trip: ${vs(formatDuration(best.durationS), formatDuration(next.durationS))}.`
  }
}

function miles(route: PlannedRoute, key: keyof RiskMiles): string {
  return `${route.riskMiles[key].toFixed(1)} mi`
}
