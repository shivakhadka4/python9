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
    """Demonstrate valid model creation and validation error handling."""
    print("Space Station Data Validation")
    print("=" * 40)

    try:
        # Pydantic automatically coerces ISO-8601 strings to datetime
        # and numeric strings/ints to float when valid.
        station = SpaceStation(
            station_id="ISS001",
            name="International Space Station",
            crew_size=6,
            power_level=85.5,
            oxygen_level=92.3,
            last_maintenance="2026-10-15T08:30:00Z",
        )
        status_label = "Operational" if station.is_operational else "Offline"
        print("Valid station created:")
        print(f"ID: {station.station_id}")
        print(f"Name: {station.name}")
        print(f"Crew: {station.crew_size} people")
        print(f"Power: {station.power_level}%")
        print(f"Oxygen: {station.oxygen_level}%")
        print(f"Status: {status_label}")
    except ValidationError as exc:
        print("Unexpected validation error on valid station:")
        print(exc)

    print("=" * 40)
    print("Expected validation error:")

    try:
        SpaceStation(
            station_id="BAD01",
            name="Overcrowded Outpost",
            crew_size=25,
            power_level=75.0,
            oxygen_level=90.0,
            last_maintenance=datetime.now(),
        )
    except ValidationError as exc:
        for err in exc.errors():
            print(err["msg"])


if __name__ == "__main__":
    main()
