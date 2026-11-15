"""Input validation for the API, and the domain -> JSON (camelCase) conversion."""

from datetime import UTC, datetime, timedelta

from rest_framework import serializers

from planner.domain.geometry import METERS_PER_MILE
from planner.service import Plan, PlanRequest

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


def plan_to_json(plan: Plan) -> dict:
    return {
        "generatedAt": _time(plan.generated_at),
        "routes": [
            {
                "id": planned.id,
                "label": planned.label,
                "geometry": [_coordinates(p) for p in planned.route.points],
                "distanceMi": _miles(planned.route.distance_m / METERS_PER_MILE),
                "durationS": round(planned.route.duration_s),
                "arrivalAt": _time(planned.arrival),
                "checkpoints": [
                    {
                        "mile": _miles(c.mile),
                        "coordinates": _coordinates(c.coordinates),
                        "eta": _time(c.eta),
                        "coversMi": [_miles(c.covers_mi[0]), _miles(c.covers_mi[1])],
                    }
                    for c in planned.checkpoints
                ],
            }
            for planned in plan.routes
        ],
    }


def _time(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _miles(value: float) -> float:
    return round(value, 1)


def _coordinates(point: tuple[float, float]) -> list[float]:
    # 5 decimals is about 1 m, plenty for drawing and for the weather lookup.
    return [round(point[0], 5), round(point[1], 5)]
