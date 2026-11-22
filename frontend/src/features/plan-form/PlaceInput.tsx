import { useQuery } from '@tanstack/react-query'
import { useId, useState } from 'react'
import { searchPlaces, type Place } from '../../lib/api'
import { useDebouncedValue } from '../../lib/useDebouncedValue'

const SEARCH_DEBOUNCE_MS = 300

type Props = {
  label: string
  value: Place | null
  onChange: (place: Place | null) => void
}

/** Text box with HERE place suggestions. Only a chosen suggestion counts as a value. */
export function PlaceInput({ label, value, onChange }: Props) {
  const id = useId()
  const [text, setText] = useState(value?.label ?? '')
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)
  const query = useDebouncedValue(text.trim(), SEARCH_DEBOUNCE_MS)

  const search = useQuery({
    queryKey: ['places', query],
    queryFn: ({ signal }) => searchPlaces(query, signal),
    enabled: isOpen && query.length > 0,
    staleTime: 10 * 60 * 1000,
  })
  // While the debounce is still waiting, the results belong to older text; never offer those.
  const isCurrent = query === text.trim()
  const places = (isCurrent && search.data?.places) || []
  const showList = isOpen && text.trim().length > 0

  function choose(place: Place) {
    onChange(place)
    setText(place.label)
    setIsOpen(false)
  }

  function onKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (!showList) return
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((i) => Math.max(0, Math.min(i + 1, places.length - 1)))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((i) => Math.max(i - 1, 0))
    } else if (event.key === 'Enter') {
      // Inside an open list, Enter picks a place; it must not submit the form.
      event.preventDefault()
      if (places[activeIndex]) choose(places[activeIndex])
    } else if (event.key === 'Escape') {
      setIsOpen(false)
    }
  }

  return (
    <div className="relative">
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-slate-700">
        {label}
      </label>
      <input
        id={id}
        role="combobox"
        aria-expanded={showList}
        aria-controls={`${id}-list`}
        aria-activedescendant={showList && places[activeIndex] ? `${id}-${activeIndex}` : undefined}
        autoComplete="off"
        placeholder="City or address"
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
        value={text}
        onChange={(event) => {
          setText(event.target.value)
          setIsOpen(true)
          setActiveIndex(0)
          if (value) onChange(null) // typing again un-chooses the place
        }}
        onFocus={() => setIsOpen(true)}
        onBlur={() => setIsOpen(false)}
        onKeyDown={onKeyDown}
      />
      {showList && (
        <ul
          id={`${id}-list`}
          role="listbox"
          className="absolute z-10 mt-1 w-full overflow-hidden rounded-lg border border-slate-200 bg-white text-sm shadow-lg"
        >
          {isCurrent && search.isError ? (
            <li className="px-3 py-2 text-red-700">{search.error.message}</li>
          ) : places.length === 0 ? (
            <li className="px-3 py-2 text-slate-500">
              {!isCurrent || search.isFetching ? 'Searching…' : 'No places found'}
            </li>
          ) : (
            places.map((place, index) => (
              <li
                key={`${place.label}-${place.lon}-${place.lat}`}
                id={`${id}-${index}`}
                role="option"
                aria-selected={index === activeIndex}
                className={`cursor-pointer px-3 py-2 ${index === activeIndex ? 'bg-slate-100' : ''}`}
                // mousedown, not click: click fires after the input's blur has closed the list.
                onMouseDown={(event) => {
                  event.preventDefault()
                  choose(place)
                }}
                onMouseEnter={() => setActiveIndex(index)}
              >
                {place.label}
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  )
}
