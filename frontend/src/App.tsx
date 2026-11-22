import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { createPlan, type PlannedRoute } from './lib/api'
import type { HeatmapVariable } from './lib/heatmap'
import { ForecastControls } from './features/forecast/ForecastControls'
import { MapView } from './features/map/MapView'
import { PlanForm } from './features/plan-form/PlanForm'
import { Recommendation } from './features/routes/Recommendation'
import { RouteList } from './features/routes/RouteList'

const NO_ROUTES: PlannedRoute[] = []

export default function App() {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null)
  const [hour, setHour] = useState(0)
  const [variable, setVariable] = useState<HeatmapVariable>('risk')
  const planning = useMutation({
    mutationFn: createPlan,
    onSuccess: (plan) => {
      setSelectedRouteId(plan.ranking.recommendedRouteId)
      setHour(0)
    },
  })
  const plan = planning.data
  // With no safe route there is nothing to drive, so no route is drawn or listed.
  const hasSafeRoute = Boolean(plan?.ranking.recommendedRouteId)

  return (
    // Phones: map on top, panel below. From md up: panel on the left, map filling the rest.
    <div className="flex h-dvh flex-col md:flex-row">
      <aside className="min-h-0 flex-1 space-y-6 overflow-y-auto border-slate-200 bg-white p-4 md:w-96 md:flex-none md:border-r md:p-6">
        <header>
          <h1 className="text-lg font-medium text-slate-900">Weather-Aware Truck Routing</h1>
          <p className="mt-1 text-sm text-slate-500">
            Up to three truck routes, weather at every checkpoint, the safest one recommended
          </p>
        </header>
        <PlanForm
          isSubmitting={planning.isPending}
          onSubmit={(request) => planning.mutate(request)}
        />
        {planning.isError && (
          <p role="alert" className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-800">
            {planning.error.message}
          </p>
        )}
        {plan && <Recommendation plan={plan} />}
        {plan && hasSafeRoute && (
          <RouteList plan={plan} selectedRouteId={selectedRouteId} onSelect={setSelectedRouteId} />
        )}
      </aside>
      <main className="relative order-first h-[50dvh] shrink-0 md:order-none md:h-auto md:flex-1">
        <MapView
          routes={plan && hasSafeRoute ? plan.routes : NO_ROUTES}
          heatmap={plan?.heatmap ?? null}
          hour={hour}
          variable={variable}
          selectedRouteId={selectedRouteId}
          onSelectRoute={setSelectedRouteId}
        />
        {planning.isPending && (
          <div
            role="status"
            className="absolute inset-x-0 top-1/2 mx-auto w-fit -translate-y-1/2 rounded-full bg-white/95 px-4 py-2 text-sm text-slate-700 shadow"
          >
            Finding routes and weather…
          </div>
        )}
        {plan && (
          <ForecastControls
            startsAt={plan.heatmap.startsAt}
            lastHour={plan.heatmap.hours - 1}
            hour={hour}
            onHourChange={setHour}
            variable={variable}
            onVariableChange={setVariable}
          />
        )}
      </main>
    </div>
  )
}
