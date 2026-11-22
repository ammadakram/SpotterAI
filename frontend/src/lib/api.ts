// Types and calls for the two backend endpoints. Shapes follow docs/ARCHITECTURE.md.

// Production: the backend's own address (set in Vercel). Development: empty, so requests
// go to this server and Vite's proxy forwards /api to Django.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export type LonLat = [number, number]

export type Place = { label: string; lon: number; lat: number }

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'SEVERE' | 'NO_TRAVEL' | 'NO_FORECAST'

export type Checkpoint = {
  mile: number
  coordinates: LonLat
  eta: string
  coversMi: [number, number]
  risk: RiskLevel
  isLoadEscalated: boolean
  /** null when there is no forecast for the checkpoint's hour */
  conditions: { wind: RiskLevel; rain: RiskLevel; snow: RiskLevel } | null
  weather: { windMph: number; gustMph: number | null; rainInHr: number; snowInHr: number } | null
  noForecastReason: string | null
}

export type Stretch = {
  level: RiskLevel
  fromMi: number
  toMi: number
  startsAt: string
  endsAt: string
}

export type RiskMiles = {
  low: number
  moderate: number
  high: number
  severe: number
  noTravel: number
  unknown: number
}

export type PlannedRoute = {
  id: string
  label: string
  geometry: LonLat[]
  distanceMi: number
  durationS: number
  arrivalAt: string
  isDrivable: boolean
  riskMiles: RiskMiles
  averageRisk: number
  stretches: Stretch[]
  checkpoints: Checkpoint[]
}

export type DecidedBy =
  'SEVERE_MILES' | 'HIGH_MILES' | 'AVERAGE_RISK' | 'DURATION' | 'ONLY_DRIVABLE'

export type Ranking = {
  orderedRouteIds: string[]
  recommendedRouteId: string | null
  decidedBy: DecidedBy | null
}

export type HeatmapCell = {
  center: LonLat
  /** Risk score per hour: 0 Low … 4 No travel; null = no forecast for that hour */
  risk: (number | null)[]
  windMph: (number | null)[]
  rainInHr: (number | null)[]
  snowInHr: (number | null)[]
}

export type Heatmap = {
  /** Hour 0: the hour that contains the time of planning */
  startsAt: string
  hours: number
  cellSizeDeg: number
  cells: HeatmapCell[]
}

export type Plan = {
  generatedAt: string
  routes: PlannedRoute[]
  ranking: Ranking
  heatmap: Heatmap
}

export type PlanRequest = {
  origin: Place
  destination: Place
  departureAt: string
  loadLb: number
  spacingMi: number
}

/** An error the user should see, with the server's message when it sent one. */
export class ApiError extends Error {
  readonly code: string

  constructor(code: string, message: string) {
    super(message)
    this.code = code
  }
}

export function searchPlaces(query: string, signal?: AbortSignal): Promise<{ places: Place[] }> {
  return request(`${API_BASE_URL}/api/places?${new URLSearchParams({ q: query })}`, { signal })
}

export function createPlan(body: PlanRequest): Promise<Plan> {
  return request(`${API_BASE_URL}/api/plans`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, init)
  } catch (error) {
    if (init.signal?.aborted) throw error
    throw new ApiError('NETWORK_ERROR', 'Could not reach the server. Check your connection.')
  }

  const body = await response.json().catch(() => undefined)
  if (!response.ok) {
    // Our API always sends { error: { code, message } }; anything else came from a proxy or crash.
    const error = body?.error
    if (error?.code && error?.message) throw new ApiError(error.code, error.message)
    throw new ApiError(
      `HTTP_${response.status}`,
      `The server answered with status ${response.status}.`,
    )
  }
  if (body === undefined)
    throw new ApiError('BAD_RESPONSE', 'The server sent a response we could not read.')
  return body as T
}
