import type { FeatureCollection, Polygon } from 'geojson'
import type { Heatmap } from './api'
import { RISK_COLOURS } from './risk'

export type HeatmapVariable = 'risk' | 'windMph' | 'rainInHr' | 'snowInHr'

/** Property prefix per variable: hour h of wind is `w${h}`, and so on. */
export const PROPERTY_PREFIX: Record<HeatmapVariable, string> = {
  risk: 'r',
  windMph: 'w',
  rainInHr: 'p',
  snowInHr: 's',
}

export const VARIABLE_LABELS: Record<HeatmapVariable, string> = {
  risk: 'Risk',
  windMph: 'Wind',
  rainInHr: 'Rain',
  snowInHr: 'Snow',
}

/**
 * Colour steps per variable: [lower bound, colour]. Risk scores 0–4 map to the risk colours.
 * Wind, rain and snow use the brief's bands for that variable alone (no load rule), in the
 * same colours, so one scale means the same everywhere. Display only; the backend decides risk.
 */
export const HEATMAP_STEPS: Record<
  HeatmapVariable,
  { from: number; colour: string; label: string }[]
> = {
  risk: [
    { from: 0, colour: RISK_COLOURS.LOW, label: 'Low' },
    { from: 1, colour: RISK_COLOURS.MODERATE, label: 'Moderate' },
    { from: 2, colour: RISK_COLOURS.HIGH, label: 'High' },
    { from: 3, colour: RISK_COLOURS.SEVERE, label: 'Severe' },
    { from: 4, colour: RISK_COLOURS.NO_TRAVEL, label: 'No travel' },
  ],
  windMph: [
    { from: 0, colour: RISK_COLOURS.LOW, label: '< 25 mph' },
    { from: 25, colour: RISK_COLOURS.MODERATE, label: '25–34' },
    { from: 35, colour: RISK_COLOURS.HIGH, label: '35–44' },
    { from: 45, colour: RISK_COLOURS.SEVERE, label: '45–54' },
    { from: 55, colour: RISK_COLOURS.NO_TRAVEL, label: '≥ 55' },
  ],
  rainInHr: [
    { from: 0, colour: RISK_COLOURS.LOW, label: '< 0.10 in/hr' },
    { from: 0.1, colour: RISK_COLOURS.MODERATE, label: '0.10–0.25' },
    { from: 0.25, colour: RISK_COLOURS.HIGH, label: '0.25–0.50' },
    { from: 0.5, colour: RISK_COLOURS.SEVERE, label: '0.50–1.00' },
    { from: 1.0001, colour: RISK_COLOURS.NO_TRAVEL, label: '> 1.00' },
  ],
  snowInHr: [
    { from: 0, colour: RISK_COLOURS.LOW, label: '< 0.5 in/hr' },
    { from: 0.5, colour: RISK_COLOURS.MODERATE, label: '0.5–1.0' },
    { from: 1, colour: RISK_COLOURS.HIGH, label: '1.0–2.0' },
    { from: 2, colour: RISK_COLOURS.SEVERE, label: '2.0–3.0' },
    { from: 3.0001, colour: RISK_COLOURS.NO_TRAVEL, label: '> 3.0' },
  ],
}

type CellProperties = Record<string, number | null>

/**
 * One square per cell, with every hour of every variable as a flat property (r0…r48, w0…w48,
 * p0…p48, s0…s48). The map uploads this once; moving the slider only changes which property
 * the paint expression reads.
 */
export function heatmapGeoJson(heatmap: Heatmap): FeatureCollection<Polygon, CellProperties> {
  const half = heatmap.cellSizeDeg / 2
  return {
    type: 'FeatureCollection',
    features: heatmap.cells.map((cell) => {
      const [lon, lat] = cell.center
      const properties: CellProperties = {}
      for (const variable of Object.keys(PROPERTY_PREFIX) as HeatmapVariable[]) {
        cell[variable].forEach((value, hour) => {
          properties[`${PROPERTY_PREFIX[variable]}${hour}`] = value
        })
      }
      return {
        type: 'Feature',
        properties,
        geometry: {
          type: 'Polygon',
          coordinates: [
            [
              [lon - half, lat - half],
              [lon + half, lat - half],
              [lon + half, lat + half],
              [lon - half, lat + half],
              [lon - half, lat - half],
            ],
          ],
        },
      }
    }),
  }
}
