import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { createPlan, type PlannedRoute } from './lib/api'
import { MapView } from './features/map/MapView'
import { PlanForm } from './features/plan-form/PlanForm'
import { Recommendation } from './features/routes/Recommendation'
import { RouteList } from './features/routes/RouteList'

const NO_ROUTES: PlannedRoute[] = []

export default function App() {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null)
  const planning = useMutation({
    mutationFn: createPlan,
    onSuccess: (plan) => setSelectedRouteId(plan.ranking.recommendedRouteId),
  })
  const plan = planning.data
  // With no safe route there is nothing to drive, so no route is drawn or listed.
  const hasSafeRoute = Boolean(plan?.ranking.recommendedRouteId)

  return (
    <div className="flex h-screen">
      <aside className="w-96 shrink-0 space-y-6 overflow-y-auto border-r border-slate-200 bg-white p-6">
        <h1 className="text-lg font-semibold text-slate-900">Weather-Aware Truck Routing</h1>
        <PlanForm
          isSubmitting={planning.isPending}
          onSubmit={(request) => planning.mutate(request)}
        />
        {planning.isError && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
            {planning.error.message}
          </p>
        )}
        {plan && <Recommendation plan={plan} />}
        {plan && hasSafeRoute && (
          <RouteList plan={plan} selectedRouteId={selectedRouteId} onSelect={setSelectedRouteId} />
        )}
      </aside>
      <main className="relative flex-1">
        <MapView
          routes={plan && hasSafeRoute ? plan.routes : NO_ROUTES}
          selectedRouteId={selectedRouteId}
          onSelectRoute={setSelectedRouteId}
        />
      </main>
    </div>
  )
}
