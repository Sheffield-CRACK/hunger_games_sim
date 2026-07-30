import random

from equipment import Equipment
from events import (
    EventAlly,
    EventBase,
    EventDrink,
    EventEnemy,
    EventFight,
    EventFood,
    EventGetEquipment,
    EventMutts,
    EventSponsorGift,
    EventUseEquipment,
    EventExposure,
    EventBloodbath,
    EventForage,
)
from tribute import Tribute


class GameMaker:
    tributes: list[Tribute]
    events: list[type[EventBase]]
    equipment: dict[Equipment, int]

    def __init__(self, tributes: list[Tribute]):
        self.tributes = tributes
        self.equipment = {
            # Non-exhaustible equipment
            Equipment(name="Knife", fighting_bonus=2, charges=-1, weight=1): 5,
            Equipment(name="Sword", fighting_bonus=3, charges=-1, weight=2): 1,
            Equipment(name="Axe", fighting_bonus=2, charges=-1, weight=3): 3,
            Equipment(name="Trident", fighting_bonus=3, charges=-1, weight=3): 1,
            Equipment(name="Tarp", comfort_bonus=2, charges=-1, weight=2): 3,
            Equipment(name="Windbreaker", comfort_bonus=2, charges=-1, weight=1): 2,
            Equipment(name="Socks", comfort_bonus=1, charges=-1, weight=0): 3,
            Equipment(name="Rope", comfort_bonus=1, charges=-1, weight=1): 3,
            Equipment(name="Hammock", comfort_bonus=3, charges=-1, weight=2): 2,
            Equipment(name="Backpack", charges=-1, weight=0): 2,
            # Exhaustible equipment
            Equipment(name="Bow and Arrows", fighting_bonus=3, charges=6, weight=2): 2,
            Equipment(name="Blowgun", fighting_bonus=1, charges=12, weight=1): 6,
            Equipment(name="First Aid Kit", health_bonus=5, charges=1, weight=1): 3,
            Equipment(name="Canteen", thirst_bonus=5, charges=3, comfort_bonus=-1, weight=1): 3,
            Equipment(name="Rations", hunger_bonus=2, charges=2, weight=1): 3,
            Equipment(name="Soup", hunger_bonus=2, thirst_bonus=2, charges=1, weight=1): 3,
            Equipment(name="Adrenaline", health_bonus=-1, fighting_bonus=1, weight=0): 2,
        }
        self.events = [
            EventFight,
            EventAlly,
            EventEnemy,
            EventMutts,
            EventFood,
            EventDrink,
            EventGetEquipment,
            EventUseEquipment,
            EventSponsorGift,
            EventExposure,
            EventForage,
        ]
        self.day = 0
        self.dead_tributes: list[tuple[Tribute, int]] = []

    @property
    def living_tributes(self) -> list[Tribute]:
        return [tribute for tribute in self.tributes if not tribute.is_dead]

    def print_tributes(self):
        print(f"{len(self.living_tributes)}/{len(self.tributes)} tributes in the game:")
        for tribute in self.living_tributes:
            print(tribute)

    def execute_events(self):
        # Group tributes by location
        location_groups = {}
        for tribute in self.tributes:
            coords_key = tuple(tribute.coords)
            if coords_key not in location_groups:
                location_groups[coords_key] = []
            location_groups[coords_key].append(tribute)

        for location, tributes_at_location in location_groups.items():
            print("~~~~~~~~~~~~~~~")
            print(f"Location {location}:")
            print(
                f"{len(tributes_at_location)} "
                f"tribute{'s' if len(tributes_at_location) != 1 else ''} present:"
                f" {', '.join([tribute.name for tribute in tributes_at_location])}"
            )
            remaining_tributes = tributes_at_location.copy()
            while len(remaining_tributes) > 0:
                # select a random event that has enough participants remaining
                valid_events = [
                    event
                    for event in self.events
                    if len(remaining_tributes) >= event.num_participants
                ]

                # randomly select a valid event type
                event = random.choice(valid_events)

                # select tributes for this event
                if event.num_participants == -1:
                    # all remaining tributes participate
                    selected_tributes = remaining_tributes.copy()
                else:
                    selected_tributes = random.sample(remaining_tributes, k=event.num_participants)

                # execute the event
                affected_tributes = event(self, selected_tributes).execute()

                # remove selected tributes from remaining tributes
                for tribute in affected_tributes:
                    remaining_tributes.remove(tribute)
        print("~~~~~~~~~~~~~~~")

    def progress_time(self) -> bool:
        self.day += 1
        print(f"Day {self.day}")
        print("~~~~~~~~~~~~~~~")

        # copy who's current alive
        currently_alive = self.living_tributes.copy()

        # shuffle the tributes
        random.shuffle(self.tributes)

        # On day 1, run events first (initial bloodbath at cornucopia), then movement
        # On subsequent days, movement happens first, then events
        if self.day == 1:
            print("The tributes gather at the cornucopia...")
            self.print_tributes()

            # execute bloodbath first on day 1
            EventBloodbath(self, self.tributes).execute()

            print("Tributes scatter from the cornucopia...")

            # Now progress time (movement) after events on day 1
            number_alive = len(self.living_tributes)
            for tribute in self.tributes:
                # if everyone else dies mid-turn, end the game
                if number_alive == 1:
                    self.game_over()
                    return False

                # skip dead people
                if tribute.is_dead:
                    continue

                stays_alive = tribute.progress_time()
                if not stays_alive:
                    number_alive -= 1
        else:
            # progress time for each tribute (movement happens first on day 2+)
            print("Progressing time...")
            number_alive = len(self.living_tributes)
            for tribute in self.tributes:
                # if everyone else dies mid-turn, end the game
                if number_alive == 1:
                    self.game_over()
                    return False

                # skip dead people
                if tribute.is_dead:
                    continue

                stays_alive = tribute.progress_time()
                if not stays_alive:
                    number_alive -= 1

            self.print_tributes()

            # execute events after movement on day 2+
            self.execute_events()

        # Print current living tributes
        self.print_tributes()

        # Find who died this round
        died_today = [tribute for tribute in currently_alive if tribute.is_dead]
        if len(died_today) == 0:
            print("Everyone survived today!")
        else:
            print(f"{len(died_today)} tributes died today:")
            for tribute in died_today:
                self.dead_tributes.append((tribute, self.day))
                print(f"{tribute.name} is dead!")

        # Check for game over
        if len(self.living_tributes) == 1:
            self.game_over()
            return False
        elif len(self.living_tributes) == 0:
            print("All tributes are dead! No winner :(")
            return False

        # Wait for user to continue
        print("~~~~~~~~~~~~~~~")
        while "I SAID (y/n)":
            reply = str(input('Continue? (y/n): ')).lower().strip()
            if reply[0] == 'y':
                return True
            if reply[0] == 'n':
                return False

    def game_over(self):
        print("Game Over")
        print(f"Winner: {self.living_tributes[0].name} :D")
        for tribute, day in self.dead_tributes:
            print(f"{tribute.name} died on day {day}")

    def run_game(self):
        print("Starting Hunger Games Simulation!")
        print("~~~~~~~~~~~~~~~")
        print("Initial Tributes:")
        self.print_tributes()
        print("~~~~~~~~~~~~~~~")
        while self.progress_time():
            pass
