import { setWorkerUrl } from 'maplibre-gl'
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import 'maplibre-gl/dist/maplibre-gl.css'
import Map from 'react-map-gl/maplibre'

// MapLibre looks for its worker next to its own module, which Vite moves when bundling.
// Pointing it at the file explicitly works the same in dev and in the production build.
setWorkerUrl(maplibreWorkerUrl)

// Light, key-free base map so the risk colours stand out.
const BASE_MAP_STYLE = 'https://tiles.openfreemap.org/styles/positron'

// Centre of the contiguous US.
const INITIAL_VIEW = { longitude: -98.5, latitude: 39.5, zoom: 3.6 }

export function MapView() {
  return <Map initialViewState={INITIAL_VIEW} mapStyle={BASE_MAP_STYLE} />
}
