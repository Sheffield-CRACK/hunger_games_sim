from __future__ import annotations

import random

TRIBUTE_TRAITS = [
    "Strong",
    "Hunter",
    "Sneaky",
    "Ranged Fighter",
    "Strategic",
    "Intelligent",
    "Popular",
    "Healer",
    "Tracker",
    "Coward",
]


class Tribute:
    name: str
    district: int
    rank: int
    trait: list[str]
    enemies: list[Tribute]
    allies: list[Tribute]
    hunger: float
    thirst: float
    _health: float
    comfort: float
    coords: list[int]

    def __init__(
        self,
        name: str,
        district: int,
        rank: int,
        trait: list[str] | None = None,
        hunger: int = 12,
        thirst: int = 12,
        health: int = 12,
        comfort: int = 0,
        coords: list[int] | None = None,
    ):
        """
        Create a new Tribute

        Parameters
        ----------
        name : str
            The tribute's name.
        district : int
            District that the tribute is part of.
        rank : int
            The tribute's fighting rank.
        trait : list[str], optional
            A list of traits to assign to the tribute. Chooses a 1-3 random traits.
        hunger : int, default: 12
            The tribute's init.
        thirst : int, default: 12
            The tribute's initial hydration level.
        health : int, default: 12
            The tribute's initial health.
        coords : list[int], optional
            The tribute's position.
        """
        self.name = name
        self.district = district
        self.rank = rank

        # Determine base traits from the provided argument (None -> random)
        if trait is None:
            traits = random.sample(TRIBUTE_TRAITS, k=random.randint(1, 3))
        elif isinstance(trait, str):
            traits = [trait]
        else:
            traits = list(trait)

        # If tribute is from districts 1, 2, or 4, ensure they have the 'Career' trait
        if self.district in (1, 2, 4):
            if "Career" not in traits:
                traits = ["Career"] + traits

        # Preserve order but ensure uniqueness
        unique_traits: list[str] = []
        for t in traits:
            if t not in unique_traits:
                unique_traits.append(t)

        self.trait = unique_traits

        self._enemies: list[Tribute] = []
        self._allies: list[Tribute] = []
        self.hunger = hunger
        self.thirst = thirst
        self._health = health
        self.comfort = comfort
        self.coords = [0, 0] if coords is None else coords
        self.equipment = []

    def __str__(self) -> str:
        string = f"{self.name} ({self.hunger}/{self.thirst}/{self.health}/{self.comfort}, {self.fighting_score})"
        string += f", {self.coords}\n"

        # Traits
        string += " - Traits:\n"
        trait_str = ", ".join(self.trait) if len(self.trait) > 0 else "None"
        string += f"   - {trait_str}\n"

        # Equipment
        string += " - Equipment:\n"
        if len(self.equipment) == 0:
            string += "   - None\n"
        else:
            equipment_string = ""
            for equipment in self.equipment:
                equipment_string += f"{equipment}, "
            equipment_string = equipment_string[:-2]  # remove trailing comma
            string += f"   - {equipment_string}\n"

        # Allies and enemies
        string += " - Allies:\n"
        if len(self.allies) == 0:
            string += "   - None\n"
        else:
            allies_string = ""
            for ally in self.allies:
                allies_string += f"{ally.name}, "
            allies_string = allies_string[:-2]  # remove trailing comma
            string += f"   - {allies_string}\n"

        string += " - Enemies:\n"
        if len(self.enemies) == 0:
            string += "   - None\n"
        else:
            enemies_string = ""
            for enemy in self.enemies:
                enemies_string += f"{enemy.name}, "
            enemies_string = enemies_string[:-2]  # remove trailing comma
            string += f"   - {enemies_string}\n"

        return string

    # Health
    @property
    def health(self) -> float:
        return self._health

    def set_health(self, new_health):
        self._health = new_health
        if new_health <= 0:
            print(f"{self.name} has died!")

    def adjust_health(self, adjust_health):
        self.set_health(self.health + adjust_health)

    @property
    def is_dead(self) -> bool:
        return self.health <= 0

    @property
    def is_alive(self) -> bool:
        return not self.is_dead

    def kill(self):
        self.set_health(0)

    # Alliances and enemies management
    @property
    def allies(self) -> list[Tribute]:
        return [tribute for tribute in self._allies if tribute.is_alive]

    @allies.setter
    def allies(self, new_allies: list[Tribute]) -> None:
        for ally in new_allies:
            self.add_ally(ally)

    def add_ally(self, other: Tribute) -> None:
        if other == self:
            return
        if other in self._allies:
            return

        if other in self._enemies:
            self._enemies.remove(other)

        self._allies += [other]
        print(f"{self.name} now sees {other.name} as an ally!")

    def remove_ally(self, other: Tribute) -> None:
        if other in self._allies:
            self._allies.remove(other)
        print(f"{self.name} no longer sees {other.name} as an ally!")

    @property
    def enemies(self) -> list[Tribute]:
        return [tribute for tribute in self._enemies if tribute.is_alive]

    @enemies.setter
    def enemies(self, new_enemies: list[Tribute]) -> None:
        for enemy in new_enemies:
            self.add_enemy(enemy)

    def add_enemy(self, other: Tribute) -> None:
        if other == self:
            return
        if other in self._enemies:
            return

        if other in self._allies:
            self._allies.remove(other)

        self._enemies += [other]
        print(f"{self.name} now sees {other.name} as an enemy!")

    def remove_enemy(self, other: Tribute) -> None:
        if other in self._enemies:
            self._enemies.remove(other)
        print(f"{self.name} no longer sees {other.name} as an enemy!")

    def is_allied_with(self, other: Tribute) -> bool:
        return other in self._allies

    def is_enemies_with(self, other: Tribute) -> bool:
        return other in self._enemies

    @property
    def fighting_score(self) -> float:
        """Calculate a fighting score."""
        fighting_score = self.rank + self.hunger + self.thirst + self.health

        # Traits that increase fighting score:
        if "Career" in self.trait:
            fighting_score += 2
        elif "Strong" in self.trait:
            fighting_score += 1
        elif "Ranged Fighter" in self.trait:
            fighting_score += 1

        # Equipment bonuses
        equipment_bonus = 0
        for item in self.equipment:
            if item.fighting_bonus > equipment_bonus:
                equipment_bonus = item.fighting_bonus
        fighting_score += equipment_bonus

        return fighting_score

    def progress_time(self) -> bool:
        """
        This function deals with the effects of time progressing

        Returns a bool indicating if the tribute is alive.
        """
        # do nothing if tribute is already dead
        if self.is_dead:
            return False

        self.hunger -= 1
        self.thirst -= 1

        # if the tributes hunger goes below zero, health decreases
        if self.hunger <= 0:
            self.adjust_health(self.hunger - 1)

        # if thirst goes below 0, the tribute dies
        if self.thirst < 0:
            self.kill()

        # randomly move to new coords
        if random.random() < 0.5:
            for i in range(2):
                # limit of 2 assumes 5x5 grid
                if self.coords[i] == 2:
                    self.coords[i] += random.randint(-1, 0)
                elif self.coords[i] == -2:
                    self.coords[i] += random.randint(0, 1)
                else:
                    self.coords[i] += random.randint(-1, 1)

        return self.is_alive
