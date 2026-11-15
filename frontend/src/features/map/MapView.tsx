import { setWorkerUrl, type ExpressionSpecification } from 'maplibre-gl'
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import type { FeatureCollection } from 'geojson'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useEffect, useMemo, useRef } from 'react'
import Map, { Layer, Source, type MapLayerMouseEvent, type MapRef } from 'react-map-gl/maplibre'
import type { Plan } from '../../lib/api'
import { boundsOf } from '../../lib/geo'

// MapLibre looks for its worker next to its own module, which Vite moves when bundling.
// Pointing it at the file explicitly works the same in dev and in the production build.
setWorkerUrl(maplibreWorkerUrl)

// Light, key-free base map so the risk colours stand out.
const BASE_MAP_STYLE = 'https://tiles.openfreemap.org/styles/positron'

// Centre of the contiguous US.
const INITIAL_VIEW = { longitude: -98.5, latitude: 39.5, zoom: 3.6 }

const SELECTED_COLOUR = '#2563eb'
const OTHER_COLOUR = '#94a3b8'

type Props = {
  plan: Plan | undefined
  selectedRouteId: string | null
  onSelectRoute: (routeId: string) => void
}

export function MapView({ plan, selectedRouteId, onSelectRoute }: Props) {
  const mapRef = useRef<MapRef>(null)

  // Built once per plan. Selecting a route changes only paint and filter expressions below,
  // so MapLibre never re-uploads the geometry.
  const routes = useMemo(() => routesGeoJson(plan), [plan])
  const checkpoints = useMemo(() => checkpointsGeoJson(plan), [plan])

  useEffect(() => {
    if (!plan) return
    const bounds = boundsOf(plan.routes.flatMap((route) => route.geometry))
    mapRef.current?.fitBounds(bounds, { padding: 60, duration: 800 })
  }, [plan])

  const isSelected: ExpressionSpecification = ['==', ['get', 'id'], selectedRouteId ?? '']

  function onClick(event: MapLayerMouseEvent) {
    const routeId = event.features?.[0]?.properties?.id
    if (typeof routeId === 'string') onSelectRoute(routeId)
  }

  return (
    <Map
      ref={mapRef}
      initialViewState={INITIAL_VIEW}
      mapStyle={BASE_MAP_STYLE}
      interactiveLayerIds={['routes']}
      onClick={onClick}
      cursor="auto"
    >
      <Source id="routes" type="geojson" data={routes}>
        <Layer
          id="routes"
          type="line"
          layout={{
            'line-join': 'round',
            'line-cap': 'round',
            'line-sort-key': ['case', isSelected, 1, 0],
          }}
          paint={{
            'line-color': ['case', isSelected, SELECTED_COLOUR, OTHER_COLOUR],
            'line-width': ['case', isSelected, 5, 3],
          }}
        />
      </Source>
      <Source id="checkpoints" type="geojson" data={checkpoints}>
        <Layer
          id="checkpoints"
          type="circle"
          filter={['==', ['get', 'routeId'], selectedRouteId ?? '']}
          paint={{
            'circle-radius': 4,
            'circle-color': '#ffffff',
            'circle-stroke-color': '#1e293b',
            'circle-stroke-width': 1.5,
          }}
        />
      </Source>
    </Map>
  )
}

function routesGeoJson(plan: Plan | undefined): FeatureCollection {
  return {
    type: 'FeatureCollection',
    features: (plan?.routes ?? []).map((route) => ({
      type: 'Feature',
      properties: { id: route.id },
      geometry: { type: 'LineString', coordinates: route.geometry },
    })),
  }
}

function checkpointsGeoJson(plan: Plan | undefined): FeatureCollection {
  return {
    type: 'FeatureCollection',
    features: (plan?.routes ?? []).flatMap((route) =>
      route.checkpoints.map((checkpoint) => ({
        type: 'Feature' as const,
        properties: { routeId: route.id, mile: checkpoint.mile },
        geometry: { type: 'Point' as const, coordinates: checkpoint.coordinates },
      })),
    ),
  }
}
