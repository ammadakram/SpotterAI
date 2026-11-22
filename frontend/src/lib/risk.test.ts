import { describe, expect, it } from 'vitest'
import type { Plan, PlannedRoute, Ranking } from './api'
import { recommendationReason } from './risk'

function route(id: string, overrides: Partial<PlannedRoute> = {}): PlannedRoute {
  return {
    id,
    label: `Route ${id}`,
    geometry: [],
    distanceMi: 100,
    durationS: 7200,
    arrivalAt: '2026-11-16T16:00:00Z',
    isDrivable: true,
    riskMiles: { low: 100, moderate: 0, high: 0, severe: 0, noTravel: 0, unknown: 0 },
    averageRisk: 0,
    stretches: [],
    checkpoints: [],
    ...overrides,
  }
}

function plan(routes: PlannedRoute[], ranking: Ranking): Plan {
  const heatmap = { startsAt: '2026-11-16T12:00:00Z', hours: 49, cellSizeDeg: 0.5, cells: [] }
  return { generatedAt: '2026-11-16T12:00:00Z', routes, ranking, heatmap }
}

const miles = (severe: number, high: number) => ({
  low: 0,
  moderate: 0,
  high,
  severe,
  noTravel: 0,
  unknown: 0,
})

describe('recommendationReason', () => {
  it('compares the deciding number with the runner-up', () => {
    const result = recommendationReason(
      plan([route('A', { riskMiles: miles(10, 0) }), route('B', { riskMiles: miles(40, 0) })], {
        orderedRouteIds: ['A', 'B'],
        recommendedRouteId: 'A',
        decidedBy: 'SEVERE_MILES',
      }),
    )
    expect(result).toBe('Fewest Severe miles: 10.0 mi vs 40.0 mi on Route B')
  })

  it('names the tie that came before the deciding criterion', () => {
    const result = recommendationReason(
      plan([route('A', { riskMiles: miles(5, 10) }), route('B', { riskMiles: miles(5, 40) })], {
        orderedRouteIds: ['A', 'B'],
        recommendedRouteId: 'A',
        decidedBy: 'HIGH_MILES',
      }),
    )
    expect(result).toBe('Same Severe miles, fewer High miles: 10.0 mi vs 40.0 mi on Route B')
  })

  it('uses travel time when risk is equal', () => {
    const result = recommendationReason(
      plan([route('A', { durationS: 3600 }), route('B', { durationS: 5400 })], {
        orderedRouteIds: ['A', 'B'],
        recommendedRouteId: 'A',
        decidedBy: 'DURATION',
      }),
    )
    expect(result).toBe('Equal risk, shorter trip: 1 h 0 min vs 1 h 30 min on Route B')
  })

  it('does not claim a shorter trip when everything is equal', () => {
    const result = recommendationReason(
      plan([route('A'), route('B')], {
        orderedRouteIds: ['A', 'B'],
        recommendedRouteId: 'A',
        decidedBy: 'DURATION',
      }),
    )
    expect(result).toBe('Equal on risk and travel time; listed first by the routing service')
  })

  it('says when the routing service found only one route', () => {
    const result = recommendationReason(
      plan([route('A')], {
        orderedRouteIds: ['A'],
        recommendedRouteId: 'A',
        decidedBy: 'ONLY_DRIVABLE',
      }),
    )
    expect(result).toBe('The only route found between these places')
  })

  it('explains a lone drivable route', () => {
    const result = recommendationReason(
      plan([route('A'), route('B', { isDrivable: false })], {
        orderedRouteIds: ['A'],
        recommendedRouteId: 'A',
        decidedBy: 'ONLY_DRIVABLE',
      }),
    )
    expect(result).toBe('The only route without No Travel conditions')
  })

  it('has nothing to say when no route is drivable', () => {
    const result = recommendationReason(
      plan([route('A', { isDrivable: false })], {
        orderedRouteIds: [],
        recommendedRouteId: null,
        decidedBy: null,
      }),
    )
    expect(result).toBeNull()
  })
})
