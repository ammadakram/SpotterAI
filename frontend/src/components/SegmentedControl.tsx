type Option<T> = { value: T; label: string }

type Props<T extends string | number> = {
  /** Radio group name; must be unique on the page. */
  name: string
  options: Option<T>[]
  value: T
  onChange: (value: T) => void
  /** Accessible name when no surrounding <legend> labels the group. */
  label?: string
}

/** A row of buttons where exactly one is chosen. Real radio inputs, so keyboard and screen
 *  readers work as for any radio group. */
export function SegmentedControl<T extends string | number>({
  name,
  options,
  value,
  onChange,
  label,
}: Props<T>) {
  return (
    <div
      role="radiogroup"
      aria-label={label}
      className="flex rounded-lg border border-slate-300 p-0.5"
    >
      {options.map((option) => (
        <label
          key={option.value}
          className="flex-1 cursor-pointer whitespace-nowrap rounded-md px-2 py-1.5 text-center text-sm text-slate-600 has-checked:bg-slate-900 has-checked:text-white has-focus-visible:ring-2 has-focus-visible:ring-slate-400"
        >
          <input
            type="radio"
            name={name}
            value={option.value}
            checked={option.value === value}
            onChange={() => onChange(option.value)}
            className="sr-only"
          />
          {option.label}
        </label>
      ))}
    </div>
  )
}
