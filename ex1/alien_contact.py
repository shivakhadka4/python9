from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    """Supported categories of reported alien contact."""

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """Validated alien contact report with cross-field business rules."""

    contact_id: str = Field(..., min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(..., min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(..., ge=0.0, le=10.0)
    duration_minutes: int = Field(..., ge=1, le=1440)
    witness_count: int = Field(..., ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_contact_rules(self) -> "AlienContact":
        """Enforce cross-field integrity rules across the full report."""
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')

        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")

        if self.contact_type == ContactType.TELEPATHIC and self.witness_count < 3:
            raise ValueError("Telepathic contact requires at least 3 witnesses")

        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                "Strong signals (greater than 7.0) should include received messages"
            )

        return self


def main() -> None:
    """Demonstrate valid and invalid alien contact report validation."""
    print("Alien Contact Log Validation")
    print("=" * 38)

    try:
        report = AlienContact(
            contact_id="AC_2024_001",
            timestamp="2024-06-15T22:30:00Z",
            location="Area 51, Nevada",
            contact_type=ContactType.RADIO,
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli",
        )
        print("Valid contact report:")
        print(f"ID: {report.contact_id}")
        print(f"Type: {report.contact_type.value}")
        print(f"Location: {report.location}")
        print(f"Signal: {report.signal_strength}/10")
        print(f"Duration: {report.duration_minutes} minutes")
        print(f"Witnesses: {report.witness_count}")
        if report.message_received is not None:
            print(f"Message:'{report.message_received}'")
    except ValidationError as exc:
        print("Unexpected validation error:")
        print(exc)

    print("=" * 38)
    print("Expected validation error:")

    try:
        AlienContact(
            contact_id="AC_2024_002",
            timestamp="2024-06-16T01:15:00Z",
            location="Sedona, Arizona",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=4.2,
            duration_minutes=20,
            witness_count=1,
        )
    except ValidationError as exc:
        for err in exc.errors():
            print(err["msg"])


if __name__ == "__main__":
    main()
