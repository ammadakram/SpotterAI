import { useEffect, useState } from 'react'
import { SegmentedControl } from '../../components/SegmentedControl'
import { formatTime } from '../../lib/format'
import { VARIABLE_LABELS, type HeatmapVariable } from '../../lib/heatmap'

const PLAY_STEP_MS = 400
const HOUR_MS = 60 * 60 * 1000

type Props = {
  startsAt: string
  lastHour: number
  hour: number
  onHourChange: (hour: number) => void
  variable: HeatmapVariable
  onVariableChange: (variable: HeatmapVariable) => void
}

/** Slider over the forecast hours, with play, and the heatmap variable picker. */
export function ForecastControls({
  startsAt,
  lastHour,
  hour,
  onHourChange,
  variable,
  onVariableChange,
}: Props) {
  const [wantsToPlay, setWantsToPlay] = useState(false)
  // Phones only: the layer picker folds away so the panel covers less of a small map.
  const [isOpen, setIsOpen] = useState(false)
  // Playing stops by itself at the last hour, without another state update.
  const isPlaying = wantsToPlay && hour < lastHour

  useEffect(() => {
    if (!isPlaying) return
    const timer = setTimeout(() => onHourChange(hour + 1), PLAY_STEP_MS)
    return () => clearTimeout(timer)
  }, [isPlaying, hour, onHourChange])

  function togglePlay() {
    if (!isPlaying && hour >= lastHour) onHourChange(0) // play again from the start
    setWantsToPlay(!isPlaying)
  }

  const time = new Date(new Date(startsAt).getTime() + hour * HOUR_MS).toISOString()

  return (
    <div className="absolute inset-x-2 top-2 mx-auto max-w-xl space-y-2 rounded-xl bg-white/95 px-3 py-2 text-sm shadow md:inset-x-4 md:top-4 md:px-4 md:py-3">
      <div className="flex items-center gap-2 md:gap-3">
        <button
          type="button"
          onClick={togglePlay}
          aria-label={isPlaying ? 'Pause' : 'Play'}
          className="grid size-8 shrink-0 place-items-center rounded-full bg-slate-900 text-white transition-colors hover:bg-slate-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
          {isPlaying ? <PauseIcon /> : <PlayIcon />}
        </button>
        <input
          type="range"
          min={0}
          max={lastHour}
          value={hour}
          onChange={(event) => {
            setWantsToPlay(false)
            onHourChange(Number(event.target.value))
          }}
          aria-label="Forecast hour"
          className="min-w-0 flex-1 accent-slate-900"
        />
        <div className="shrink-0 whitespace-nowrap text-right tabular-nums text-slate-700 sm:w-40">
          {formatTime(time)} <span className="text-slate-500 max-sm:hidden">+{hour} h</span>
        </div>
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          aria-controls="forecast-layers"
          className="flex shrink-0 items-center gap-1 rounded-lg px-2 py-1 text-slate-600 transition-colors hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-blue-600 md:hidden"
        >
          {VARIABLE_LABELS[variable]}
          <ChevronIcon isOpen={isOpen} />
        </button>
      </div>
      <div
        id="forecast-layers"
        className={`${isOpen ? 'flex' : 'hidden'} items-center gap-2 md:flex`}
      >
        <span className="text-slate-600">Corridor weather</span>
        <SegmentedControl
          name="heatmap-variable"
          label="Corridor weather"
          options={(Object.keys(VARIABLE_LABELS) as HeatmapVariable[]).map((option) => ({
            value: option,
            label: VARIABLE_LABELS[option],
          }))}
          value={variable}
          onChange={onVariableChange}
        />
      </div>
    </div>
  )
}

const ICON = {
  width: 16,
  height: 16,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
}

function PlayIcon() {
  return (
    <svg {...ICON}>
      <path d="M7 4.5v15l12-7.5z" fill="currentColor" />
    </svg>
  )
}

function PauseIcon() {
  return (
    <svg {...ICON}>
      <path d="M8 5v14M16 5v14" strokeWidth={3} />
    </svg>
  )
}

function ChevronIcon({ isOpen }: { isOpen: boolean }) {
  return (
    <svg {...ICON} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}>
      <path d="M6 9l6 6 6-6" />
    </svg>
  )
}
