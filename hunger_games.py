from __future__ import annotations

import random
from abc import ABC, abstractmethod


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
    coords: list[int]

    def __init__(
        self,
        name: str, 
        district: int,
        rank: int,
        trait: list[str] = None,
        enemies: list[Tribute] = [],
        allies: list[Tribute] = [],
        hunger: int = 12,
        thirst: int = 12,
        health: int = 12,
        coords: list[int]|None = None,
    ):
        self.name = name
        self.district = district
        self.rank = rank
        # Available non-career traits
        available_traits = ['Strong', 'Hunter', 'Sneaky', 'Ranged Fighter', 'Strategic', 'Intelligent', 'Popular', 'Healer', 'Tracker', 'Coward']

        # Determine base traits from the provided argument (None -> random)
        if trait is None:
            traits = random.sample(available_traits, k=random.randint(1, 3))
        elif isinstance(trait, str):
            traits = [trait]
        else:
            traits = list(trait)

        # If tribute is from districts 1, 2, or 4, ensure they have the 'Career' trait
        if self.district in (1, 2, 4):
            if 'Career' not in traits:
                traits.insert(0, 'Career')

        # Preserve order but ensure uniqueness
        unique_traits: list[str] = []
        for t in traits:
            if t not in unique_traits:
                unique_traits.append(t)

        self.trait = unique_traits

        self.enemies = enemies
        self.allies = allies
        self.hunger = hunger
        self.thirst = thirst
        self._health = health
        self.coords = [0,0] if coords is None else coords

    def __str__(self) -> str:
        traits_str = ', '.join(self.trait)
        return f"{self.name} ({self.hunger}/{self.thirst}/{self.health}, {self.fighting_score}), {self.coords} - Traits: {traits_str}"


    @property
    def health(self)-> float:
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

    @property
    def fighting_score(self) -> float:
        """Calculate a fighting score."""
        if 'Career' in self.trait:
            fighting_score = self.rank + self.hunger + self.thirst + self.health + 2
        elif 'Strong' in self.trait:
            fighting_score = self.rank + self.hunger + self.thirst + self.health + 1
        elif 'Ranged Fighter' in self.trait:
            fighting_score = self.rank + self.hunger + self.thirst + self.health + 1
        else:
            fighting_score = self.rank + self.hunger + self.thirst + self.health
        return fighting_score

    def progress_time(self) -> bool:
        '''
        This function deals with the effects of time progressing
        '''
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
                    self.coords[i] += random.randint(-1,0)
                elif self.coords[i] == -2:
                    self.coords[i] += random.randint(0,1)
                else:
                    self.coords[i] += random.randint(-1,1)

        return self.is_alive


class EventBase(ABC):

    tributes: list[Tribute]

    def __init__(self, tributes:list[Tribute]):
        self.tributes = tributes

    @abstractmethod
    def execute(self):
        ...

class EventFight(EventBase):

    def execute(self):
        print('A fight is happening!')
        players = random.sample(self.tributes, k=2)

        print('Fighting between:')
        for player in players:
            print(f' - {player.name} (rank: {player.rank}, health: {player.health})')

        # Choose who is strongest
        if players[0].fighting_score == players[1].fighting_score:
            print('It was a draw!')
            players[0].adjust_health(-1)
            players[1].adjust_health(-1)
            return
        sorted_players = sorted(players, key=lambda x: x.fighting_score, reverse=True)
        stronger, weaker = sorted_players[0], sorted_players[1]

        # Choose who wins the fight
        difference = stronger.fighting_score - weaker.fighting_score
        if difference >= 6:
            print(f'{stronger.name} is much stronger than {weaker.name}!')
            winner, loser = stronger, weaker
        elif 0 < difference < 6:
            # Draw, but stronger player has a slight advantage
            if random.random() < 0.7:
                print(f'{stronger.name} is slightly stronger than {weaker.name}!')
                winner, loser = stronger, weaker
            else:
                print(f'{weaker.name} managed to overpower {stronger.name}!')
                winner, loser = weaker, stronger
        else:
            raise ValueError("Logic error in fight calculation: stronger person isn't stronger than the weaker person!")

        if random.random() < 0.5:
            print(f'{winner.name} killed {loser.name}!')
            loser.kill()
        else:
            print(f'{loser.name} managed to escape from {winner.name}!')
            loser.adjust_health(-1)


class EventMutts(EventBase):

    num_participants = -1
    mutts_list = ['tracker jackers', 'jabberjays', 'carnivorous squirrels', 'wolf mutts', 'monkey mutts', 'feral undergrads']

    def execute(self):

        mutt = random.choice(self.mutts_list)
        mutt_zone = [random.randint(-2,2), random.randint(-2,2)]
        print(f"{mutt.capitalize()} have been released into area {mutt_zone}!")

        tributes = [tribute for tribute in self.tributes if tribute.coords == mutt_zone]
        num_victims = len(tributes)
        if num_victims == 0:
            print('But nobody is there womp womp')
        for tribute in tributes:
            d6 = random.randint(1,6)

            if d6 in [1]:
                # killed outright
                print(f"{tribute.name} was killed by the {mutt}!")
                tribute.kill()
            if d6 in [2,3]:
                # severe injury
                tribute.adjust_health(-5)
                print(f"{tribute.name} was severely wounded by the {mutt}!")
            if d6 in [4,5]:
                # wounded!
                tribute.adjust_health(-3)
                print(f"{tribute.name} was slightly wounded by the {mutt}!")
            if d6 in [6]:
                # escaped!
                tribute.adjust_health(-1)
                print(f"{tribute.name} escaped the {mutt}!")


class EventFood(EventBase):

    def execute(self):
        tribute = random.sample(self.tributes, k=1)
        print(f'{tribute[0].name} found some food!')
        tribute[0].hunger += 2


class EventDrink(EventBase):

    def execute(self):
        tribute = random.sample(self.tributes, k=1)
        print(f'{tribute[0].name} found some water!')
        tribute[0].thirst += 2

class GameMaker():

    tributes: list[Tribute]
    events: list[type[EventBase]]

    def __init__(self, tributes:list[Tribute]):
        self.tributes = tributes
        self.events = [
            EventFight,
            EventMutts,
            EventFood,
            EventDrink,
        ]
        self.day = 0
        self.dead_tributes: list[tuple[Tribute, int]] = []

    @property
    def living_tributes(self) -> list[Tribute]:
        return [tribute for tribute in self.tributes if not tribute.is_dead]

    def print_tributes(self):
        print(f'{len(self.living_tributes)}/{len(self.tributes)} tributes in the game:')
        for tribute in self.living_tributes:
            print(tribute)

    def progress_time(self) -> bool:
        self.day += 1
        print(f'Day {self.day}')
        print('~~~~~~~~~~~~~~~')

        # copy who's current alive
        currently_alive = self.living_tributes.copy()

        # progress time for each tribute
        print('Progressing time...')
        for tribute in self.tributes:
            tribute.progress_time()
        self.print_tributes()

        # execute events
        remaining_tributes = self.living_tributes.copy()
        while len(remaining_tributes) > 0:
            # randomly select an event type
            event = random.choice(self.events)

            # check if enough tributes remain for this event
            if len(remaining_tributes) < event.num_participants:
                continue

            print('~~~~~~~~~~~~~~~')

            # select tributes for this event
            if event.num_participants == -1:
                # all remaining tributes participate
                selected_tributes = remaining_tributes.copy()
            else:
                selected_tributes = random.sample(remaining_tributes, k=event.num_participants)

            # execute the event
            event(selected_tributes).execute()

            # remove selected tributes from remaining tributes
            for tribute in selected_tributes:
                remaining_tributes.remove(tribute)
        print('~~~~~~~~~~~~~~~')

        # Check for game over
        if len(self.living_tributes) == 1:
            print('Game Over')
            print(f'Winner: {self.living_tributes[0].name} :D')
            for tribute, day in self.dead_tributes:
                print(f'{tribute.name} died on day {day}')
            return False

        # Print current living tributes
        self.print_tributes()

        # Find who died this round
        died_today = [
            tribute
            for tribute in currently_alive
            if tribute.is_dead
        ]
        if len(died_today) == 0:
            print('Everyone survived today!')
        else:
            print(f'{len(died_today)} tributes died today:')
            for tribute in died_today:
                self.dead_tributes.append((tribute, self.day))
                print(f'{tribute.name} is dead!')
        # Wait for user to continue
        print('~~~~~~~~~~~~~~~')
        input('Continue? :')

        return True

    def run_game(self):
        print('Starting Hunger Games Simulation!')
        print('~~~~~~~~~~~~~~~')
        print('Initial Tributes:')
        self.print_tributes()
        print('~~~~~~~~~~~~~~~')
        while self.progress_time():
            pass

if __name__ == '__main__':
    tributes = [
        Tribute(name='Katniss Everdeen', district=12, rank=12),
        Tribute(name='Peeta Mellark', district=12, rank=6),
        Tribute(name='Gale Hawthorne', district=12, rank=2),
        Tribute(name='Haymitch Abernathy', district=12, rank=1),
        Tribute(name='Effie Trinket', district=12, rank=3),
        Tribute(name='Cinna', district=12, rank=4),
        Tribute(name='Prim Everdeen', district=12, rank=5),
        Tribute(name='Finnick Odair', district=4, rank=8),
        Tribute(name='Johanna Mason', district=7, rank=9),
        Tribute(name='Clove', district=2, rank=10),
        Tribute(name='Cato', district=2, rank=11),
        Tribute(name='Rue', district=11, rank=7),
        Tribute(name='Thresh', district=11, rank=13),
        Tribute(name='Foxface', district=5, rank=14),
        Tribute(name='Marvel', district=1, rank=15),
    ]
    game = GameMaker(tributes)
    game.run_game()
