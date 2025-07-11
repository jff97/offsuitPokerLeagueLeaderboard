from dataclasses import dataclass, fields
from typing import Dict, Any

@dataclass
class PlayerRoundEntry:
    player_name: str
    round_id: str
    bar_name: str
    points: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dict with snake_case keys."""
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerRoundEntry":
        """Create object from dict with snake_case keys."""
        init_args = {field.name: data[field.name] for field in fields(cls)}
        return cls(**init_args)

    def unique_id(self) -> Dict[str, Any]:
        def nameof(fn):
            return fn.__code__.co_names[0]

        unique_fields = [
            nameof(lambda: self.player_name),
            nameof(lambda: self.round_id),
            nameof(lambda: self.bar_name),
        ]
        return {field: getattr(self, field) for field in unique_fields}
