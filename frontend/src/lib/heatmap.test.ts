import { describe, expect, it } from 'vitest'
import type { Heatmap } from './api'
import { heatmapGeoJson } from './heatmap'

const hours = 49
const series = (value: (h: number) => number | null) =>
  Array.from({ length: hours }, (_, h) => value(h))

const heatmap: Heatmap = {
  startsAt: '2026-11-16T12:00:00Z',
  hours,
  cellSizeDeg: 0.5,
  cells: [
    {
      center: [-97.25, 32.75],
      risk: series((h) => (h === 12 ? 3 : h === 48 ? null : 0)),
      windMph: series((h) => 10 + h),
      rainInHr: series((h) => h / 100),
      snowInHr: series(() => 0),
    },
  ],
}

describe('heatmapGeoJson', () => {
  const [square] = heatmapGeoJson(heatmap).features

  it('draws each cell as a square of cellSizeDeg around its centre', () => {
    expect(square.geometry).toEqual({
      type: 'Polygon',
      coordinates: [
        [
          [-97.5, 32.5],
          [-97.0, 32.5],
          [-97.0, 33.0],
          [-97.5, 33.0],
          [-97.5, 32.5],
        ],
      ],
    })
  })

  it('puts hour h of every variable in a flat property, so the map can read it by name', () => {
    expect(square.properties).toMatchObject({ r12: 3, w12: 22, p12: 0.12, s12: 0 })
    expect(square.properties.r0).toBe(0)
  })

  it('keeps a missing forecast as null, never 0 (which would draw as Low)', () => {
    expect(square.properties.r48).toBeNull()
  })
})
