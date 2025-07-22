class NameClash:
    def __init__(self, name: str, clash: str = None, clash_description: str = None):
        self.name = name
        self.clash = clash
        self.clash_description = clash_description

    def to_dict(self):
        return {
            'name': self.name,
            'clash': self.clash,
            'clash_description': self.clash_description
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d.get('name'),
            clash=d.get('clash'),
            clash_description=d.get('clash_description')
        )
    def unique_id(self):
        """Returns the unique identifier for this NameInfo (the name itself)."""
        return self.name
