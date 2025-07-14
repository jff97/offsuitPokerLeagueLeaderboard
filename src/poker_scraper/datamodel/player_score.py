from dataclasses import dataclass, fields
from typing import Dict, Any

@dataclass(frozen=True)
class PlayerScore:
    player_name: str
    points: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dict using dataclass fields."""
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerScore":
        """Create object from dict using dataclass fields."""
        init_args = {field.name: data[field.name] for field in fields(cls)}
        return cls(**init_args)
