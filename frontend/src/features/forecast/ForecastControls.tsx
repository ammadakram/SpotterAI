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
    <div className="absolute inset-x-4 top-4 mx-auto max-w-xl space-y-2 rounded-md bg-white/95 px-4 py-3 text-sm shadow">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={togglePlay}
          aria-label={isPlaying ? 'Pause' : 'Play'}
          className="size-8 shrink-0 rounded-full bg-slate-900 text-white hover:bg-slate-800"
        >
          {isPlaying ? '❚❚' : '▶'}
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
          className="flex-1 accent-slate-900"
        />
        <div className="w-40 shrink-0 whitespace-nowrap text-right tabular-nums text-slate-700">
          {formatTime(time)} <span className="text-slate-500">+{hour} h</span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-slate-600">Corridor weather:</span>
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
