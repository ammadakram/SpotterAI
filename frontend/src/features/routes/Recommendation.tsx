import type { Plan } from '../../lib/api'
import { recommendationReason } from '../../lib/risk'

export function Recommendation({ plan }: { plan: Plan }) {
  const recommended = plan.routes.find((route) => route.id === plan.ranking.recommendedRouteId)
  if (!recommended) {
    return (
      <div role="status" className="rounded-md bg-purple-50 px-4 py-3 text-sm text-purple-950">
        <div className="font-medium">No safe route for this departure</div>
        <p className="mt-1">
          Every route meets No Travel conditions. Try a later departure or a lighter load.
        </p>
      </div>
    )
  }
  const reason = recommendationReason(plan)
  return (
    <div role="status" className="rounded-md bg-green-50 px-4 py-3 text-sm text-green-950">
      <div className="font-medium">Recommended: {recommended.label}</div>
      {reason && <p className="mt-1">{reason}</p>}
    </div>
  )
}
