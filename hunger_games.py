from __future__ import annotations

from abc import ABC, abstractmethod
import random
import json
import time

class Tribute:
    name: str
    district: int
    rank: int
    trait: str
    enemies: list[Tribute]
    allies: list[Tribute]
    hunger: float
    thirst: float
    _health: float

    def __init__(
        self,
        name: str,
        district: int,
        rank: int,
        trait: str,
        enemies: list[Tribute] = [],
        allies: list[Tribute] = [],
        hunger: int = 12,
        thirst: int = 12,
        health: int = 12,
    ):
        self.name = name
        self.district = district
        self.rank = rank
        self.trait = trait
        self.enemies = enemies
        self.allies = allies
        self.hunger = hunger
        self.thirst = thirst
        self._health = health

    def __str__(self) -> str:
        return f"{self.name} ({self.hunger}/{self.thirst}/{self.health}, {self.fighting_score})"

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
        return self.rank + self.hunger + self.thirst + self.health

    def progress_time(self) -> bool:
        '''
        This function deals with the effects of time progressing

        Returns a bool indicating if the tribute is alive.
        '''
        # do nothing if tribute is already dead
        if self.is_dead:
            return False

        self.hunger -= 1
        self.thirst -= 1

        # if the tributes hunger goes below zero, health decreases
        if self.hunger <= 0:
            self.adjust_health(self.hunger - 1)

        # if thiradjust_st goelow 0, the tribute dies
        if self.thirst < 0:
            self.kill()

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

    mutts_list = ['tracker jackers', 'jabberjays', 'carnivorous squirrelu', 'wolf mutts', 'monkey mutts']

    def execute(self):

        mutt = random.choice(self.mutts_list)
        print(f"{mutt} have been released in the arena!")

        tribute: Tribute = random.choice(self.tributes)
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
            tribute.adjust_health(-3)
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

    @property
    def living_tributes(self) -> list[Tribute]:
        return [tribute for tribute in self.tributes if not tribute.is_dead]

    def progress_time(self) -> bool:
        print('Progressing time...')
        self.day += 1
        print(f'Day {self.day}')

        # shuffle the tributes
        random.shuffle(self.tributes)

        # progress time for each tribute
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

        # print living tributes
        print('Living tributes:')
        for tribute in self.living_tributes:
            print(tribute)

        # randomly select an event type
        event: type[EventBase] = random.choice(self.events)

        # select participating tributes
        event(self.living_tributes).execute()

        if len(self.living_tributes) == 1:
            self.game_over()
            return False

        print(f'{len(self.living_tributes)} tributes remaining')
        for tribute in self.living_tributes:
            print(tribute)

        print('~~~~~~~~~~~~~~~')
        input('Continue? :')

        return True
    
    def game_over(self):
        print('Game Over')
        print(f'Winner: {self.living_tributes[0].name} :D')

    def run_game(self):
        while self.progress_time():
            pass

if __name__ == '__main__':
    with open('tributes.json', encoding='utf-8') as f_in:
        tributes_data = json.load(f_in)

    if not isinstance(tributes_data, list):
        raise ValueError('tributes.json must contain a list of objects')
    
    tributes: list[Tribute] = []
    for d in tributes_data:
        tributes += [Tribute(
            name=d['name'],
            district=d['district'],
            rank= d['rank'],
            trait=d.get('trait'), # if not given, set to None
        )]

    game = GameMaker(tributes)
    game.run_game()
