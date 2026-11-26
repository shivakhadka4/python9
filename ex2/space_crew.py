from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    """Supported crew ranks ordered by authority."""

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """Validated individual space mission crew member."""

    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    """Validated space mission with nested crew and safety rules."""

    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: list[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission_safety(self) -> "SpaceMission":
        """Enforce mission-level and crew-composition safety rules."""
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')

        has_command = any(
            member.rank in (Rank.COMMANDER, Rank.CAPTAIN) for member in self.crew
        )
        if not has_command:
            raise ValueError("Mission must have at least one Commander or Captain")

        if self.duration_days > 365:
            experienced_count = sum(
                1 for member in self.crew if member.years_experience >= 5
            )
            if experienced_count * 2 < len(self.crew):
                raise ValueError(
                    "Long missions (over 365 days) need 50% experienced crew (5+ years)"
                )

        if any(not member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")

        return self


def main() -> None:
    """Demonstrate valid and invalid space mission crew validation."""
    print("Space Mission Crew Validation")
    print("=" * 41)

    valid_payload: dict[str, object] = {
        "mission_id": "M2024_MARS",
        "mission_name": "Mars Colony Establishment",
        "destination": "Mars",
        "launch_date": "2026-11-25T12:00:00Z",
        "duration_days": 900,
        "budget_millions": 2500.0,
        "crew": [
            CrewMember(
                member_id="CM01",
                name="Sarah Connor",
                rank=Rank.COMMANDER,
                age=42,
                specialization="Mission Command",
                years_experience=15,
            ),
            CrewMember(
                member_id="CM02",
                name="John Smith",
                rank=Rank.LIEUTENANT,
                age=34,
                specialization="Navigation",
                years_experience=8,
            ),
            CrewMember(
                member_id="CM03",
                name="Alice Johnson",
                rank=Rank.OFFICER,
                age=29,
                specialization="Engineering",
                years_experience=3,
            ),
        ],
    }

    try:
        mission = SpaceMission.model_validate(valid_payload)
        print("Valid mission created:")
        print(f"Mission: {mission.mission_name}")
        print(f"ID: {mission.mission_id}")
        print(f"Destination: {mission.destination}")
        print(f"Duration: {mission.duration_days} days")
        print(f"Budget: ${mission.budget_millions}M")
        print(f"Crew size: {len(mission.crew)}")
        print("Crew members:")
        for member in mission.crew:
            print(f"- {member.name} ({member.rank.value}) - {member.specialization}")
    except ValidationError as exc:
        print("Unexpected validation error:")
        print(exc)

    print("=" * 41)
    print("Expected validation error:")

    invalid_payload: dict[str, object] = {
        "mission_id": "M2024_FAIL",
        "mission_name": "Orbital Survey",
        "destination": "Europa",
        "launch_date": "2026-12-01T09:00:00Z",
        "duration_days": 120,
        "budget_millions": 500.0,
        "crew": [
            CrewMember(
                member_id="CM04",
                name="Bob Lee",
                rank=Rank.LIEUTENANT,
                age=31,
                specialization="Sensors",
                years_experience=6,
            ),
            CrewMember(
                member_id="CM05",
                name="Eve Park",
                rank=Rank.OFFICER,
                age=27,
                specialization="Biology",
                years_experience=5,
            ),
        ],
    }

    try:
        SpaceMission.model_validate(invalid_payload)
    except ValidationError as exc:
        for err in exc.errors():
            print(err["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
