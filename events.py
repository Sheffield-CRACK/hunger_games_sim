import random
from abc import ABC, abstractmethod
from copy import deepcopy

from equipment import Equipment
from tribute import Tribute


class EventBase(ABC):
    tributes: list[Tribute]
    num_participants: int = 1

    def __init__(self, gamemaker, tributes: list[Tribute]):
        self.gamemaker = gamemaker
        self.tributes = tributes

    @abstractmethod
    def execute(self): ...


class EventFight(EventBase):
    num_participants = 2

    def execute(self):
        # Group tributes by location
        location_groups = {}
        for tribute in self.tributes:
            coords_key = tuple(tribute.coords)
            if coords_key not in location_groups:
                location_groups[coords_key] = []
            location_groups[coords_key].append(tribute)

        # Find locations with at least 2 tributes
        valid_locations = [tributes for tributes in location_groups.values() if len(tributes) >= 2]

        if not valid_locations:
            return []

        print("A fight is happening!")

        # Pick a random location with multiple tributes
        fight_location = random.choice(valid_locations)
        players = random.sample(fight_location, k=self.num_participants)

        print("Fighting between:")
        for player in players:
            print(
                f" - {player.name} (rank: {player.rank}, health: {player.health}, fighting score: {player.fighting_score})"
            )

        # Choose who is strongest
        if players[0].fighting_score == players[1].fighting_score:
            print("It was a draw!")
            players[0].adjust_health(-1)
            players[1].adjust_health(-1)
            winner = None
            loser = None

        else:
            sorted_players = sorted(players, key=lambda x: x.fighting_score, reverse=True)
            stronger, weaker = sorted_players[0], sorted_players[1]

            # Choose who wins the fight
            difference = stronger.fighting_score - weaker.fighting_score
            if difference >= 6:
                print(f"{stronger.name} is much stronger than {weaker.name}!")
                winner, loser = stronger, weaker
            elif 0 < difference < 6:
                # Draw, but stronger player has a slight advantage
                if random.random() < 0.7:
                    print(f"{stronger.name} is slightly stronger than {weaker.name}!")
                    winner, loser = stronger, weaker
                else:
                    print(f"{weaker.name} managed to overpower {stronger.name}!")
                    winner, loser = weaker, stronger
            else:
                raise ValueError(
                    "Logic error in fight calculation: stronger person isn't stronger than the weaker person!"
                )

            if random.random() < 0.5:
                print(f"{winner.name} killed {loser.name}!")
                loser.kill()
            else:
                print(f"{loser.name} managed to escape from {winner.name}!")
                loser.adjust_health(-1)

        # Remove equipment if it has limited charges
        for player in players:
            if len(player.equipment) == 0:
                continue
            best_fighting_bonus = max([e.fighting_bonus for e in player.equipment])
            if best_fighting_bonus == 0:
                continue

            for equipment in player.equipment:
                if equipment.fighting_bonus == best_fighting_bonus:
                    print(f"{player.name} used {equipment.name} in the fight!")
                    equipment.use()
                    if equipment.is_broken:
                        print(f"{equipment.name} is gone!")
                        player.equipment.remove(equipment)
                    else:
                        print(f"{equipment.name} has {equipment.charges} uses left.")

        # If loser is dead, winner picks up their equipment
        if loser is not None and winner is not None and loser.is_dead:
            for equipment in loser.equipment:
                print(f"{winner.name} picked up {loser.name}'s {equipment.name}!")
            winner.equipment += loser.equipment
            loser.equipment = []

        return players


class EventMutts(EventBase):
    num_participants = -1
    mutts_list = [
        "tracker jackers",
        "jabberjays",
        "carnivorous squirrels",
        "wolf mutts",
        "monkey mutts",
        "feral undergrads",
    ]

    def execute(self):

        mutt = random.choice(self.mutts_list)
        mutt_zone = [random.randint(-2, 2), random.randint(-2, 2)]
        print(f"{mutt.capitalize()} have been released into area {mutt_zone}!")

        tributes = [tribute for tribute in self.tributes if tribute.coords == mutt_zone]
        if len(tributes) == 0:
            print("But nobody is there womp womp")
        for tribute in tributes:
            d6 = random.randint(1, 6)

            if d6 in [1]:
                # killed outright
                print(f"{tribute.name} was killed by the {mutt}!")
                tribute.kill()
            if d6 in [2, 3]:
                # severe injury
                tribute.adjust_health(-5)
                print(f"{tribute.name} was severely wounded by the {mutt}!")
            if d6 in [4, 5]:
                # wounded!
                tribute.adjust_health(-3)
                print(f"{tribute.name} was slightly wounded by the {mutt}!")
            if d6 in [6]:
                # escaped!
                tribute.adjust_health(-1)
                print(f"{tribute.name} escaped the {mutt}!")
        return tributes


class EventFood(EventBase):
    num_participants = 1

    def execute(self):
        tribute = random.sample(self.tributes, k=self.num_participants)
        print(f"{tribute[0].name} found some food!")
        tribute[0].hunger += 2
        return tribute


class EventDrink(EventBase):
    num_participants = 1

    def execute(self):
        tribute = random.sample(self.tributes, k=self.num_participants)[0]
        print(f"{tribute.name} found some water!")
        tribute.thirst += 2

        # Use water purifier if they have it
        used_water_purifier = False
        tribute_equipment_names = [equipment.name for equipment in tribute.equipment]
        if "Water Purifier" in tribute_equipment_names:
            print(f"{tribute.name} used a Water Purifier")
            for equipment in tribute.equipment:
                if equipment.name == "Water Purifier":
                    equipment.use()
                    used_water_purifier = True
                    if equipment.is_broken:
                        print(f"{equipment.name} is gone!")
                        tribute.equipment.remove(equipment)
                    else:
                        print(f"{equipment.name} has {equipment.charges} uses left.")
        is_bad = random.random() < 0.5
        if is_bad and not used_water_purifier:
            print(f"{tribute.name} drank from the water and got sick!")
            tribute.adjust_health(-2)
        else:
            print(f"{tribute.name} drank from the water and stayed healthy!")

        return tribute


class EventGetEquipment(EventBase):
    num_participants = 1

    def execute(self):
        tribute = random.sample(self.tributes, k=self.num_participants)[0]
        valid_equipment = [
            equipment for equipment, quantity in self.gamemaker.equipment.items() if quantity > 0
        ]
        if len(valid_equipment) == 0:
            print("No equipment left to find, womp womp!")
            return [tribute]
        equipment = random.choice(valid_equipment)
        new_equipment = deepcopy(equipment)

        # Remove one of the equipments from gamemaker inventory
        self.gamemaker.equipment[equipment] -= 1

        if new_equipment.charges != -1:
            # Exhaustible equipment
            # Check if they already have one of the same type
            already_has_one = False
            for equip in tribute.equipment:
                if equip.name == new_equipment.name:
                    already_has_one = True
                    print(f"{tribute.name} found {new_equipment.name} but already has one!")
                    equip.charges += new_equipment.charges
                    print(f"{equip.name} now has {equip.charges} uses!")
            if not already_has_one:
                print(f"{tribute.name} found equipment: {new_equipment.name}!")
                tribute.equipment.append(new_equipment)
        else:
            print(f"{tribute.name} found equipment: {new_equipment.name}!")
            tribute.equipment.append(new_equipment)
        return [tribute]


class EventUseEquipment(EventBase):
    num_participants = 1

    def execute(self):
        tributes_with_equipment = [
            tribute for tribute in self.tributes if len(tribute.equipment) > 0
        ]
        if len(tributes_with_equipment) == 0:
            return []

        tribute = random.choice(tributes_with_equipment)

        for equipment in tribute.equipment:
            if equipment.fighting_bonus > 0:
                continue

            print(f"{tribute.name} is using {equipment}).")

            # Apply equipment effects
            tribute.hunger += equipment.hunger_bonus
            tribute.thirst += equipment.thirst_bonus
            tribute.adjust_health(equipment.health_bonus)

            # Remove equipment if it has limited charges
            equipment.use()
            if equipment.is_broken:
                print(f"{equipment.name} is gone!")
                tribute.equipment.remove(equipment)
            else:
                print(f"{equipment.name} has {equipment.charges} uses left.")

        return [tribute]


class EventSponsorGift(EventBase):
    num_participants = 1
    possible_gifts = [
        Equipment(name="Medicine", health_bonus=8, charges=1),
        Equipment(name="Wine", thirst_bonus=5, charges=3),
        Equipment(name="Bread", hunger_bonus=4, charges=4),
        Equipment(name="Spile", thirst_bonus=1, charges=-1),
        Equipment(name="Water Purifier", charges=3),
        Equipment(name="Fire starter kit", charges=3),
    ]

    def execute(self):
        tribute = random.sample(self.tributes, k=self.num_participants)[0]
        gift = random.choice(self.possible_gifts)
        gift = deepcopy(gift)
        print(f"{tribute.name} received a sponsor gift: {gift}!")
        tribute.equipment.append(gift)
        return [tribute]
