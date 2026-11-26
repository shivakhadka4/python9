from datetime import datetime

from pydantic import BaseModel, Field, ValidationError


class SpaceStation(BaseModel):
    """Validated vital telemetry model for a space station."""

    station_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    crew_size: int = Field(..., ge=1, le=20)
    power_level: float = Field(..., ge=0.0, le=100.0)
    oxygen_level: float = Field(..., ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = Field(default=True)
    notes: str | None = Field(default=None, max_length=200)


def main() -> None:
    """Demonstrate valid space station creation and validation errors."""
    print("Space Station Data Validation")
    print("=" * 40)

    valid_data: dict[str, object] = {
        "station_id": "ISS001",
        "name": "International Space Station",
        "crew_size": 6,
        "power_level": 85.5,
        "oxygen_level": 92.3,
        "last_maintenance": "2026-10-15T08:30:00Z",
    }

    try:
        # Pydantic coerces ISO-8601 string timestamps into datetime objects.
        station = SpaceStation.model_validate(valid_data)
        status_text = "Operational" if station.is_operational else "Non-operational"
        print("Valid station created:")
        print(f"ID: {station.station_id}")
        print(f"Name: {station.name}")
        print(f"Crew: {station.crew_size} people")
        print(f"Power: {station.power_level}%")
        print(f"Oxygen: {station.oxygen_level}%")
        print(f"Status: {status_text}")
    except ValidationError as exc:
        print("Unexpected validation error:")
        print(exc)

    print("=" * 40)
    print("Expected validation error:")

    invalid_data: dict[str, object] = {
        "station_id": "BAD001",
        "name": "Overcrowded Station",
        "crew_size": 25,
        "power_level": 80.0,
        "oxygen_level": 90.0,
        "last_maintenance": "2026-10-15T08:30:00Z",
    }

    try:
        SpaceStation.model_validate(invalid_data)
    except ValidationError as exc:
        for err in exc.errors():
            print(err["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
