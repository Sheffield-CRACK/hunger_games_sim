from __future__ import annotations

class Trap:
    owner: str
    type: str
    damage: int
    effect: str
    def __init__(self,
                 owner: str = 'none',
                 type: str = 'standard', 
                 damage: int = 4,
                 effect: str = 'none'
            ):
                self.owner = owner
                self.type = type
                self.damage = damage
                self.effect = effect