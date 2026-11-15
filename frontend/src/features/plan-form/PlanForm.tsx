import { useState } from 'react'
import type { Place, PlanRequest } from '../../lib/api'
import { toDateTimeLocal } from '../../lib/format'
import { PlaceInput } from './PlaceInput'

const MAX_LOAD_LB = 45_000
const MAX_HOURS_AHEAD = 48
const SPACINGS_MI = [10, 25, 50]

type Props = {
  isSubmitting: boolean
  onSubmit: (request: PlanRequest) => void
}

export function PlanForm({ isSubmitting, onSubmit }: Props) {
  const [origin, setOrigin] = useState<Place | null>(null)
  const [destination, setDestination] = useState<Place | null>(null)
  // Empty means "leave now", worked out when submitting so it never goes stale.
  const [departure, setDeparture] = useState('')
  const [load, setLoad] = useState('')
  const [spacingMi, setSpacingMi] = useState(25)
  const [problem, setProblem] = useState<string | null>(null)

  // Only a hint for the date picker; the real check uses the time of submitting.
  const [openedAt] = useState(() => new Date())

  function submit(event: React.FormEvent) {
    event.preventDefault()
    const latest = hoursFrom(new Date(), MAX_HOURS_AHEAD)
    const loadLb = Number(load)
    const departureAt = departure === '' ? new Date() : new Date(departure)
    if (!origin || !destination)
      return setProblem('Choose an origin and a destination from the list.')
    if (load.trim() === '' || !Number.isInteger(loadLb) || loadLb < 0 || loadLb > MAX_LOAD_LB)
      return setProblem(
        `Load must be a whole number from 0 to ${MAX_LOAD_LB.toLocaleString('en-US')} lb.`,
      )
    if (Number.isNaN(departureAt.getTime()) || departureAt > latest)
      return setProblem(`Departure must be between now and ${MAX_HOURS_AHEAD} hours from now.`)
    setProblem(null)
    onSubmit({
      origin,
      destination,
      // A time a minute or two in the past means "leave now"; the server allows that.
      departureAt: departureAt.toISOString(),
      loadLb,
      spacingMi,
    })
  }

  return (
    <form onSubmit={submit} className="space-y-4" noValidate>
      <PlaceInput label="Origin" value={origin} onChange={setOrigin} />
      <PlaceInput label="Destination" value={destination} onChange={setDestination} />

      <div>
        <label htmlFor="departure" className="mb-1 block text-sm font-medium text-slate-700">
          Departure <span className="font-normal text-slate-500">(empty = now)</span>
        </label>
        <input
          id="departure"
          type="datetime-local"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          value={departure}
          min={toDateTimeLocal(openedAt)}
          max={toDateTimeLocal(hoursFrom(openedAt, MAX_HOURS_AHEAD))}
          onChange={(event) => setDeparture(event.target.value)}
        />
      </div>

      <div className="flex gap-3">
        <div className="flex-1">
          <label htmlFor="load" className="mb-1 block text-sm font-medium text-slate-700">
            Load (lb)
          </label>
          <input
            id="load"
            type="number"
            inputMode="numeric"
            min={0}
            max={MAX_LOAD_LB}
            step={1000}
            placeholder="e.g. 32000"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={load}
            onChange={(event) => setLoad(event.target.value)}
          />
        </div>
        <div className="flex-1">
          <label htmlFor="spacing" className="mb-1 block text-sm font-medium text-slate-700">
            Checkpoint every
          </label>
          <select
            id="spacing"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
            value={spacingMi}
            onChange={(event) => setSpacingMi(Number(event.target.value))}
          >
            {SPACINGS_MI.map((mi) => (
              <option key={mi} value={mi}>
                {mi} mi
              </option>
            ))}
          </select>
        </div>
      </div>

      {problem && <p className="text-sm text-red-700">{problem}</p>}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60"
      >
        {isSubmitting ? 'Planning…' : 'Plan routes'}
      </button>
    </form>
  )
}

function hoursFrom(date: Date, hours: number): Date {
  return new Date(date.getTime() + hours * 3600 * 1000)
}
