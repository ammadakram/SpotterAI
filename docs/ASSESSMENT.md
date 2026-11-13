# Assessment Brief — Weather-Aware Truck Routing

Source: `docs/fs-assessment-spotter.pdf` (the original wins over anything here).

## Summary
React + Django web app that helps a truck driver pick the **safest route** based on **weather, load weight, and travel time**. Third-party APIs are allowed for routing, geocoding and weather; no need to build a routing engine.

**Priority stated in the brief: correctness and clarity over extra features.**

## Inputs
- [ ] Origin & destination
- [ ] Departure date/time
- [ ] Load weight

## Required behaviour
- [ ] Generate **3 route options** using a routing API
- [ ] Sample weather every **10 / 25 / 50 miles**, using the truck's **estimated arrival time** at each checkpoint (not "now")
- [ ] Classify risk per checkpoint using the risk + load rules below
- [ ] Recommend the best route (ranking below)
- [ ] Map shows all routes, checkpoints, risk levels, ETAs, route summaries
- [ ] Weather **heatmap along the trip corridor** with a **0–48 h forecast slider**

## Risk rules (per checkpoint)
| Condition | Low | Moderate | High | Severe | No Travel |
|---|---|---|---|---|---|
| Wind | <25 mph | 25–34 | 35–44 | 45–54 | ≥55 |
| Rain | <0.10 in/hr | 0.10–0.25 | 0.25–0.50 | 0.50–1.00 | >1.00 |
| Snow | <0.5 in/hr | 0.5–1.0 | 1.0–2.0 | 2.0–3.0 | >3.0 |

Load rules:
- ≥55 mph → No Travel for any load
- 45–54 mph + >30,000 lb → No Travel
- 35–44 mph + >40,000 lb → Severe

## Recommendation ranking (in order)
1. Fewest Severe miles
2. Fewest High miles
3. Lowest average risk
4. Shortest travel time

## Deliverables
- [ ] GitHub repository
- [ ] Hosted application
- [ ] 5–10 min Loom walkthrough

## Evaluation weights
- **40%** Routes, weather, risk & recommendation logic
- **40%** UI, map & heatmap smoothness and performance
- **15%** Code quality
- **5%** Documentation & walkthrough

## Ambiguities to resolve (decide, then log in DECISIONS.md and README)
- **10 / 25 / 50 miles** — user-selectable sampling interval? (likely)
- **Overlapping band edges** (e.g. rain 0.25 is in both Moderate and High; wind 34.5 falls between bands) — need one consistent boundary rule.
- **Combining conditions** — checkpoint risk = worst of wind/rain/snow (+ load adjustment)?
- **No Travel in ranking** — the ranking never mentions it; a route with any No Travel segment should rank below all others (or be flagged as not drivable).
- **"Severe miles"** — how many miles each checkpoint represents (half the gap to neighbours, or the segment ahead).
- **"Average risk"** — numeric scale (e.g. Low=0 … No Travel=4), distance-weighted.
- **ETA source** — routing API durations are car-based unless a truck profile is used; consider truck speed adjustment.
- **Forecast horizon** — departure + trip beyond the forecast window; what to show.
- **Heatmap vs. route ETA** — slider shows the corridor at hour *h* from now (or from departure), separate from per-checkpoint ETA weather.
