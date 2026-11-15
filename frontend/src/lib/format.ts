// Display formatting. Times are shown in the viewer's own time zone.

export function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return hours === 0 ? `${minutes} min` : `${hours} h ${minutes} min`
}

export function formatMiles(miles: number): string {
  return `${Math.round(miles).toLocaleString('en-US')} mi`
}

const timeFormat = new Intl.DateTimeFormat('en-US', {
  weekday: 'short',
  hour: 'numeric',
  minute: '2-digit',
})

export function formatTime(iso: string): string {
  return timeFormat.format(new Date(iso))
}

/** The value a `datetime-local` input expects: local time, minutes precision. */
export function toDateTimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
    `T${pad(date.getHours())}:${pad(date.getMinutes())}`
  )
}
