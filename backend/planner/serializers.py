"""Input validation for the API, and the domain -> JSON (camelCase) conversion."""

from datetime import UTC, datetime, timedelta

from rest_framework import serializers

from planner.domain.geometry import METERS_PER_MILE
from planner.domain.types import RatedCheckpoint, RiskLevel
from planner.service import Plan, PlannedRoute, PlanRequest

MAX_LOAD_LB = 45_000
MAX_DEPARTURE_AHEAD = timedelta(hours=48)
# "Depart now" reaches the server a few seconds late; don't reject it for that.
DEPARTURE_GRACE = timedelta(minutes=10)
SPACINGS_MI = [10, 25, 50]


class PlaceSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=200)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    lat = serializers.FloatField(min_value=-90, max_value=90)


class PlanRequestSerializer(serializers.Serializer):
    origin = PlaceSerializer()
    destination = PlaceSerializer()
    departureAt = serializers.DateTimeField()
    loadLb = serializers.IntegerField(min_value=0, max_value=MAX_LOAD_LB)
    spacingMi = serializers.ChoiceField(choices=SPACINGS_MI)

    def validate_departureAt(self, value: datetime) -> datetime:
        now = self.context["now"]
        if not now - DEPARTURE_GRACE <= value <= now + MAX_DEPARTURE_AHEAD:
            raise serializers.ValidationError(
                "Departure must be between now and 48 hours from now."
            )
        return value

    def to_request(self) -> PlanRequest:
        data = self.validated_data
        return PlanRequest(
            origin=(data["origin"]["lon"], data["origin"]["lat"]),
            destination=(data["destination"]["lon"], data["destination"]["lat"]),
            departure=data["departureAt"],
            load_lb=data["loadLb"],
            spacing_mi=data["spacingMi"],
        )


# Wire names for the risk-mile buckets; NO_FORECAST miles are "unknown".
RISK_MILES_KEYS = {
    RiskLevel.LOW: "low",
    RiskLevel.MODERATE: "moderate",
    RiskLevel.HIGH: "high",
    RiskLevel.SEVERE: "severe",
    RiskLevel.NO_TRAVEL: "noTravel",
    RiskLevel.NO_FORECAST: "unknown",
}


def plan_to_json(plan: Plan) -> dict:
    return {
        "generatedAt": _time(plan.generated_at),
        "routes": [_route_json(planned) for planned in plan.routes],
        "ranking": {
            "orderedRouteIds": plan.ranking.ordered_route_ids,
            "recommendedRouteId": plan.ranking.recommended_route_id,
            "decidedBy": plan.ranking.decided_by,
        },
    }


def _route_json(planned: PlannedRoute) -> dict:
    assessment = planned.assessment
    return {
        "id": planned.id,
        "label": planned.label,
        "geometry": [_coordinates(p) for p in planned.route.points],
        "distanceMi": _miles(planned.route.distance_m / METERS_PER_MILE),
        "durationS": round(planned.route.duration_s),
        "arrivalAt": _time(planned.arrival),
        "isDrivable": assessment.is_drivable,
        "riskMiles": {
            key: _miles(assessment.risk_miles[level]) for level, key in RISK_MILES_KEYS.items()
        },
        "averageRisk": round(assessment.average_risk, 2),
        "stretches": [
            {
                "level": s.level,
                "fromMi": _miles(s.from_mi),
                "toMi": _miles(s.to_mi),
                "startsAt": _time(s.starts_at),
                "endsAt": _time(s.ends_at),
            }
            for s in assessment.stretches
        ],
        "checkpoints": [_checkpoint_json(rated) for rated in planned.checkpoints],
    }


def _checkpoint_json(rated: RatedCheckpoint) -> dict:
    c, risk, weather = rated.checkpoint, rated.risk, rated.weather
    return {
        "mile": _miles(c.mile),
        "coordinates": _coordinates(c.coordinates),
        "eta": _time(c.eta),
        "coversMi": [_miles(c.covers_mi[0]), _miles(c.covers_mi[1])],
        "risk": risk.level,
        "isLoadEscalated": risk.is_load_escalated,
        "conditions": None
        if risk.level == RiskLevel.NO_FORECAST
        else {"wind": risk.wind, "rain": risk.rain, "snow": risk.snow},
        "weather": None
        if weather is None
        else {
            "windMph": weather.wind_mph,
            "gustMph": weather.gust_mph,
            "rainInHr": round(weather.rain_in_hr, 3),
            "snowInHr": weather.snow_in_hr,
        },
        "noForecastReason": risk.no_forecast_reason,
    }


def _time(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _miles(value: float) -> float:
    return round(value, 1)


def _coordinates(point: tuple[float, float]) -> list[float]:
    # 5 decimals is about 1 m, plenty for drawing and for the weather lookup.
    return [round(point[0], 5), round(point[1], 5)]
