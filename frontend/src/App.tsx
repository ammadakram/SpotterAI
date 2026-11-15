import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { createPlan } from './lib/api'
import { MapView } from './features/map/MapView'
import { PlanForm } from './features/plan-form/PlanForm'
import { RouteList } from './features/routes/RouteList'

export default function App() {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null)
  const planning = useMutation({
    mutationFn: createPlan,
    onSuccess: (plan) => setSelectedRouteId(plan.routes[0]?.id ?? null),
  })
  const plan = planning.data

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
        {plan && (
          <RouteList
            routes={plan.routes}
            selectedRouteId={selectedRouteId}
            onSelect={setSelectedRouteId}
          />
        )}
      </aside>
      <main className="flex-1">
        <MapView plan={plan} selectedRouteId={selectedRouteId} onSelectRoute={setSelectedRouteId} />
      </main>
    </div>
  )
}
