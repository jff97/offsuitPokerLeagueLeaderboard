from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RoundEntry:
    player: str
    round_id: str
    bar_name: str
    points: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dict for MongoDB storage (field names capitalized)."""
        return {
            "PlayerName": self.player,
            "RoundId": self.round_id,
            "BarName": self.bar_name,
            "Points": self.points
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoundEntry":
        """Create object from MongoDB dict."""
        return cls(
            player=data["PlayerName"],
            round_id=data["RoundId"],
            bar_name=data["BarName"],
            points=data["Points"]
        )

    def unique_id(self) -> Dict[str, Any]:
        """Returns the unique identifier fields for DB upsert filtering."""
        return {
            "PlayerName": self.player,
            "RoundId": self.round_id,
            "BarName": self.bar_name
        }
