from datetime import UTC, datetime, timedelta

from planner.domain.heatmap import HEATMAP_HOURS, heatmap_frames
from planner.domain.types import HourlySeries, RiskLevel

SERIES_START = datetime(2026, 11, 16, 9, 0, tzinfo=UTC)
NOW = datetime(2026, 11, 16, 9, 20, tzinfo=UTC)
CELL = (-97.25, 32.75)
LIGHT_LOAD = 10_000


def series(hours: int = 96, **overrides) -> HourlySeries:
    """Hour i (ending SERIES_START + i h) has wind 10 + i."""
    values = {
        "wind_mph": [10.0 + i for i in range(hours)],
        "gust_mph": [20.0] * hours,
        "rain_in_hr": [0.0] * hours,
        "showers_in_hr": [0.0] * hours,
        "snow_in_hr": [0.0] * hours,
    }
    return HourlySeries(start=SERIES_START, **{**values, **overrides})


def test_starts_with_the_hour_that_contains_now_and_has_49_hours():
    heatmap = heatmap_frames({CELL: series()}, NOW, LIGHT_LOAD)

    # 9:20 is inside the hour ending 10:00, which is series hour 1.
    assert heatmap.starts_at == datetime(2026, 11, 16, 10, 0, tzinfo=UTC)
    (cell,) = heatmap.cells
    assert cell.center == CELL
    assert len(cell.wind_mph) == HEATMAP_HOURS == 49
    assert cell.wind_mph[0] == 11.0
    assert cell.wind_mph[12] == 23.0  # hour 12 = 22:00


def test_now_exactly_on_the_hour_starts_at_that_hour():
    heatmap = heatmap_frames({CELL: series()}, SERIES_START + timedelta(hours=2), LIGHT_LOAD)

    assert heatmap.starts_at == SERIES_START + timedelta(hours=2)
    assert heatmap.cells[0].wind_mph[0] == 12.0


def test_rain_includes_showers_and_snow_is_kept():
    heatmap = heatmap_frames(
        {CELL: series(rain_in_hr=[0.1] * 96, showers_in_hr=[0.2] * 96, snow_in_hr=[0.6] * 96)},
        NOW,
        LIGHT_LOAD,
    )

    cell = heatmap.cells[0]
    assert round(cell.rain_in_hr[0], 6) == 0.3
    assert cell.snow_in_hr[0] == 0.6
    assert cell.risk[0] == RiskLevel.HIGH  # rain 0.30 in/hr


def test_risk_uses_the_same_load_rules():
    windy = series(wind_mph=[40.0] * 96)

    light = heatmap_frames({CELL: windy}, NOW, 30_000).cells[0]
    heavy = heatmap_frames({CELL: windy}, NOW, 45_000).cells[0]

    assert light.risk[0] == RiskLevel.HIGH
    assert heavy.risk[0] == RiskLevel.SEVERE


def test_hours_without_a_forecast_are_no_forecast_never_low():
    # Only 20 hours of data: from hour 19 of the heatmap on there is nothing.
    heatmap = heatmap_frames({CELL: series(hours=20, wind_mph=[5.0] * 20)}, NOW, LIGHT_LOAD)

    cell = heatmap.cells[0]
    assert cell.risk[18] == RiskLevel.LOW
    assert cell.risk[19:] == [RiskLevel.NO_FORECAST] * 30
    assert cell.wind_mph[19:] == [None] * 30
