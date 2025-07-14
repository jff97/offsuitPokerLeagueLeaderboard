from dataclasses import dataclass, fields
from typing import Dict, Any, Tuple
from . import player_score

@dataclass(frozen=True)
class Round:
    round_id: str
    bar_name: str
    round_date: str  # The actual date when the round took place (YYYY-MM-DD)
    bar_id: str  # Bar identifier (not the secret token) - for data lineage
    players: Tuple[player_score.PlayerScore, ...]

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dict using dataclass fields."""
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name == "players":
                # Special handling for players tuple - convert to list of dicts
                result[field.name] = [player.to_dict() for player in value]
            else:
                result[field.name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Round":
        """Create object from dict using dataclass fields."""
        init_args = {}
        for field in fields(cls):
            if field.name == "players":
                # Special handling for players - convert list to tuple of PlayerScore objects
                players_list = [player_score.PlayerScore.from_dict(player_data) for player_data in data[field.name]]
                init_args[field.name] = tuple(players_list)
            else:
                init_args[field.name] = data[field.name]
        return cls(**init_args)

    def unique_id(self) -> Dict[str, Any]:
        """Return unique identifier for this round."""
        return {
            "round_id": self.round_id,
            "bar_name": self.bar_name
        }
