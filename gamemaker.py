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
            Equipment(name="Knife", fighting_bonus=2, charges=-1): 5,
            Equipment(name="Sword", fighting_bonus=3, charges=-1): 1,
            Equipment(name="Axe", fighting_bonus=2, charges=-1): 3,
            Equipment(name="Trident", fighting_bonus=3, charges=-1): 1,
            # Exhaustible equipment
            Equipment(name="Bow and Arrows", fighting_bonus=3, charges=6): 2,
            Equipment(name="Blowgun", fighting_bonus=1, charges=12): 6,
            Equipment(name="First Aid Kit", health_bonus=5, charges=1): 3,
            Equipment(name="Canteen", thirst_bonus=5, charges=3): 3,
            Equipment(name="Rations", hunger_bonus=2, charges=2): 3,
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
        # TODO: Should pick location first, then do events for tributes in that location
        remaining_tributes = self.living_tributes.copy()
        while len(remaining_tributes) > 0:
            print("~~~~~~~~~~~~~~~")
            # select a random event that has enough participants remaining
            valid_events = [
                event for event in self.events if len(remaining_tributes) >= event.num_participants
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

            # execute events first on day 1
            self.execute_events()

            print("~~~~~~~~~~~~~~~")
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

        print("~~~~~~~~~~~~~~~")

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
        input("Continue? :")

        return True

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
