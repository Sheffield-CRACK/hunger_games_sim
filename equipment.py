class Equipment:
    name: str
    hunger_bonus: int
    thirst_bonus: int
    health_bonus: int
    fighting_bonus: int
    comfort_bonus: int
    charges: int
    weight: int

    def __init__(
        self,
        name: str,
        hunger_bonus: int = 0,
        thirst_bonus: int = 0,
        health_bonus: int = 0,
        fighting_bonus: int = 0,
        comfort_bonus: int = 0,
        charges: int = -1,
        weight: int = 1,
    ):
        self.name = name
        self.hunger_bonus = hunger_bonus
        self.thirst_bonus = thirst_bonus
        self.health_bonus = health_bonus
        self.fighting_bonus = fighting_bonus
        self.comfort_bonus = comfort_bonus
        self.charges = charges
        self.weight = weight

    def __repr__(self) -> str:
        charges_str = "unlimited" if self.charges == -1 else f"{self.charges} uses left"
        return f"{self.name} ({charges_str})"

    @property
    def is_broken(self) -> bool:
        if self.charges == -1:  # Non-exhaustible equipment never breaks
            return False
        return self.charges <= 0

    def use(self) -> int:
        if self.charges > 0:  # Non-exhaustible equipment never removes charges
            self.charges -= 1
        return self.charges
