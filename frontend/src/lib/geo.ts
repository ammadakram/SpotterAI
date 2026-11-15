import type { LonLat } from './api'

/** [[west, south], [east, north]] around all the given points. */
export function boundsOf(points: LonLat[]): [LonLat, LonLat] {
  let [west, south, east, north] = [Infinity, Infinity, -Infinity, -Infinity]
  for (const [lon, lat] of points) {
    west = Math.min(west, lon)
    south = Math.min(south, lat)
    east = Math.max(east, lon)
    north = Math.max(north, lat)
  }
  return [
    [west, south],
    [east, north],
  ]
}
