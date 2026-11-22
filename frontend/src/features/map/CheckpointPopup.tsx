import { Popup } from 'react-map-gl/maplibre'
import type { Checkpoint } from '../../lib/api'
import { formatTime } from '../../lib/format'
import { RISK_COLOURS, RISK_LABELS } from '../../lib/risk'

type Props = { checkpoint: Checkpoint; onClose: () => void }

export function CheckpointPopup({ checkpoint, onClose }: Props) {
  const { weather, conditions } = checkpoint
  return (
    <Popup
      longitude={checkpoint.coordinates[0]}
      latitude={checkpoint.coordinates[1]}
      onClose={onClose}
      closeOnClick={false}
      closeButton={false}
      maxWidth="260px"
    >
      <div className="space-y-1 text-sm text-slate-800">
        <div className="flex items-center gap-2 font-medium">
          <span
            className="inline-block size-2.5 rounded-full"
            style={{ backgroundColor: RISK_COLOURS[checkpoint.risk] }}
          />
          {RISK_LABELS[checkpoint.risk]} · mile {Math.round(checkpoint.mile)}
        </div>
        <div className="text-slate-600">Truck here {formatTime(checkpoint.eta)}</div>
        {weather && conditions ? (
          <dl className="grid grid-cols-[auto_1fr] gap-x-3">
            <dt>Wind</dt>
            <dd>
              {weather.windMph.toFixed(0)} mph
              {weather.gustMph !== null && `, gusts ${weather.gustMph.toFixed(0)}`} ·{' '}
              {RISK_LABELS[conditions.wind]}
            </dd>
            <dt>Rain</dt>
            <dd>
              {weather.rainInHr.toFixed(2)} in/hr · {RISK_LABELS[conditions.rain]}
            </dd>
            <dt>Snow</dt>
            <dd>
              {weather.snowInHr.toFixed(2)} in/hr · {RISK_LABELS[conditions.snow]}
            </dd>
          </dl>
        ) : (
          <div className="text-slate-600">{checkpoint.noForecastReason}</div>
        )}
        {checkpoint.isLoadEscalated && (
          <div className="text-slate-600">
            Raised by the load: heavy trucks are at more risk in wind.
          </div>
        )}
      </div>
    </Popup>
  )
}
