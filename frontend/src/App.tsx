import { MapView } from './features/map/MapView'

export default function App() {
  return (
    <div className="flex h-screen">
      <aside className="w-96 shrink-0 border-r border-slate-200 bg-white p-6">
        <h1 className="text-lg font-semibold text-slate-900">Weather-Aware Truck Routing</h1>
      </aside>
      <main className="flex-1">
        <MapView />
      </main>
    </div>
  )
}
