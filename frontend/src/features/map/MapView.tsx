import { setWorkerUrl, type ExpressionSpecification } from 'maplibre-gl'
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import type { FeatureCollection } from 'geojson'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useEffect, useMemo, useRef, useState } from 'react'
import Map, { Layer, Source, type MapLayerMouseEvent, type MapRef } from 'react-map-gl/maplibre'
import type { Checkpoint, Heatmap, PlannedRoute } from '../../lib/api'
import { boundsOf } from '../../lib/geo'
import {
  HEATMAP_STEPS,
  PROPERTY_PREFIX,
  heatmapGeoJson,
  type HeatmapVariable,
} from '../../lib/heatmap'
import { RISK_COLOURS } from '../../lib/risk'
import { CheckpointPopup } from './CheckpointPopup'
import { RiskLegend } from './RiskLegend'

// MapLibre looks for its worker next to its own module, which Vite moves when bundling.
// Pointing it at the file explicitly works the same in dev and in the production build.
setWorkerUrl(maplibreWorkerUrl)

// Light, key-free base map so the risk colours stand out.
const BASE_MAP_STYLE = 'https://tiles.openfreemap.org/styles/positron'

// Centre of the contiguous US.
const INITIAL_VIEW = { longitude: -98.5, latitude: 39.5, zoom: 3.6 }

const SELECTED_COLOUR = '#2563eb'
const OTHER_COLOUR = '#94a3b8'

// Open-Meteo's licence (CC BY 4.0) requires the credit.
const ATTRIBUTION = 'Weather: <a href="https://open-meteo.com/">Open-Meteo</a>'

const CHECKPOINT_COLOUR: ExpressionSpecification = [
  'match',
  ['get', 'risk'],
  'LOW',
  RISK_COLOURS.LOW,
  'MODERATE',
  RISK_COLOURS.MODERATE,
  'HIGH',
  RISK_COLOURS.HIGH,
  'SEVERE',
  RISK_COLOURS.SEVERE,
  'NO_TRAVEL',
  RISK_COLOURS.NO_TRAVEL,
  'NO_FORECAST',
  RISK_COLOURS.NO_FORECAST,
  '#ff00ff', // a level this list doesn't know: loud magenta, never a real risk colour
]

const HEATMAP_OPACITY = 0.35
const NO_HEATMAP: FeatureCollection = { type: 'FeatureCollection', features: [] }

type Props = {
  routes: PlannedRoute[]
  heatmap: Heatmap | null
  hour: number
  variable: HeatmapVariable
  selectedRouteId: string | null
  onSelectRoute: (routeId: string) => void
}

export function MapView({
  routes,
  heatmap,
  hour,
  variable,
  selectedRouteId,
  onSelectRoute,
}: Props) {
  const mapRef = useRef<MapRef>(null)
  // Remember which routes the popup belongs to, so it disappears when a new plan arrives.
  const [popup, setPopup] = useState<{ routes: PlannedRoute[]; checkpoint: Checkpoint } | null>(
    null,
  )
  const openCheckpoint = popup?.routes === routes ? popup.checkpoint : null
  const [isPointing, setIsPointing] = useState(false)

  // Built once per plan. Selecting a route changes only paint and filter expressions below,
  // so MapLibre never re-uploads the geometry.
  const routeLines = useMemo(() => routesGeoJson(routes), [routes])
  const checkpoints = useMemo(() => checkpointsGeoJson(routes), [routes])
  const heatmapSquares = useMemo(() => (heatmap ? heatmapGeoJson(heatmap) : NO_HEATMAP), [heatmap])

  useEffect(() => {
    // Frame the routes; with no safe route there are none, so frame the corridor instead.
    const points =
      routes.length > 0
        ? routes.flatMap((route) => route.geometry)
        : (heatmap?.cells.map((cell) => cell.center) ?? [])
    if (points.length === 0) return
    const map = mapRef.current
    if (!map) return
    // The top padding keeps the trip clear of the forecast controls drawn over the map. It
    // shrinks with the map, so a short phone map still has room left for the trip.
    const height = map.getContainer().clientHeight
    map.fitBounds(boundsOf(points), {
      padding: {
        top: Math.min(130, height * 0.3),
        bottom: Math.min(40, height * 0.1),
        left: 40,
        right: 40,
      },
      duration: 800,
    })
  }, [routes, heatmap])

  const isSelected: ExpressionSpecification = ['==', ['get', 'id'], selectedRouteId ?? '']

  function onClick(event: MapLayerMouseEvent) {
    const feature = event.features?.[0]
    if (!feature) return setPopup(null)
    if (feature.layer.id === 'checkpoints') {
      const { routeId, index } = feature.properties
      const checkpoint = routes.find((r) => r.id === routeId)?.checkpoints[index]
      setPopup(checkpoint ? { routes, checkpoint } : null)
    } else {
      onSelectRoute(feature.properties.id)
    }
  }

  return (
    <Map
      ref={mapRef}
      initialViewState={INITIAL_VIEW}
      mapStyle={BASE_MAP_STYLE}
      interactiveLayerIds={['checkpoints', 'routes']}
      onClick={onClick}
      onMouseEnter={() => setIsPointing(true)}
      onMouseLeave={() => setIsPointing(false)}
      cursor={isPointing ? 'pointer' : 'grab'}
      attributionControl={{ customAttribution: ATTRIBUTION }}
    >
      {/* First, so it is drawn under the routes. Moving the slider only swaps the property
          the colour reads (r0 → r1 …): no data upload, no re-render of the squares. */}
      <Source id="heatmap" type="geojson" data={heatmapSquares}>
        <Layer
          id="heatmap"
          type="fill"
          paint={{
            'fill-color': heatmapColour(variable, hour),
            'fill-opacity': HEATMAP_OPACITY,
            'fill-outline-color': 'rgba(0, 0, 0, 0)',
          }}
        />
      </Source>
      <Source id="routes" type="geojson" data={routeLines}>
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
            'circle-radius': 5,
            'circle-color': CHECKPOINT_COLOUR,
            'circle-stroke-color': '#ffffff',
            'circle-stroke-width': 1.5,
          }}
        />
      </Source>
      {openCheckpoint && (
        <CheckpointPopup checkpoint={openCheckpoint} onClose={() => setPopup(null)} />
      )}
      <RiskLegend variable={variable} />
    </Map>
  )
}

function routesGeoJson(routes: PlannedRoute[]): FeatureCollection {
  return {
    type: 'FeatureCollection',
    features: routes.map((route) => ({
      type: 'Feature',
      properties: { id: route.id },
      geometry: { type: 'LineString', coordinates: route.geometry },
    })),
  }
}

function checkpointsGeoJson(routes: PlannedRoute[]): FeatureCollection {
  return {
    type: 'FeatureCollection',
    features: routes.flatMap((route) =>
      route.checkpoints.map((checkpoint, index) => ({
        type: 'Feature' as const,
        properties: { routeId: route.id, index, risk: checkpoint.risk },
        geometry: { type: 'Point' as const, coordinates: checkpoint.coordinates },
      })),
    ),
  }
}

function heatmapColour(variable: HeatmapVariable, hour: number): ExpressionSpecification {
  const value: ExpressionSpecification = ['get', `${PROPERTY_PREFIX[variable]}${hour}`]
  const [first, ...rest] = HEATMAP_STEPS[variable]
  return [
    'case',
    ['==', value, null],
    RISK_COLOURS.NO_FORECAST,
    ['step', value, first.colour, ...rest.flatMap((step) => [step.from, step.colour])],
  ]
}
