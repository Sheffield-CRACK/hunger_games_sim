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
    def execute(self) -> list[Tribute]: ...


class EventFight(EventBase):
    num_participants = 2

    def execute(self) -> list[Tribute]:
        # TODO: This should be in the GameMaker class, not here.
        # Instead of picking events for the tributes remaining, we should pick
        # a location with tributes in it, then pick random events for them.

        print("A fight is happening!")

        print("Fighting between:")
        players = random.sample(self.tributes, k=self.num_participants)
        for player in players:
            print(
                f" - {player.name} (rank: {player.rank}, health: {player.health}, fighting score: {player.fighting_score})"
            )

        # If they are both allied, they don't fight
        if players[0].is_allied_with(players[1]) and players[1].is_allied_with(players[0]):
            print("But they are allies, so they don't fight!")
            return players

        # If only one is allied and the other isn't, it's a betrayal!
        betrayer, betrayed = None, None
        if players[0].is_allied_with(players[1]) and not players[1].is_allied_with(players[0]):
            betrayer, betrayed = players[1], players[0]
        elif players[1].is_allied_with(players[0]) and not players[0].is_allied_with(players[1]):
            betrayer, betrayed = players[0], players[1]
        if betrayer is not None and betrayed is not None:
            # They become enemies, and the betrayed player takes damage.
            print(f"{betrayer.name} betrayed {betrayed.name}!")
            betrayed.add_enemy(betrayer)
            betrayed.adjust_health(-1)

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


class EventAlly(EventBase):
    num_participants = 2

    def execute(self) -> list[Tribute]:
        tribute1, tribute2 = random.sample(self.tributes, k=self.num_participants)
        print(f"{tribute1.name} and {tribute2.name} have become mutual allies!")
        tribute1.add_ally(tribute2)
        tribute2.add_ally(tribute1)
        return [tribute1, tribute2]


class EventEnemy(EventBase):
    num_participants = 2

    def execute(self) -> list[Tribute]:
        tribute1, tribute2 = random.sample(self.tributes, k=self.num_participants)
        print(f"{tribute1.name} and {tribute2.name} have become mutual enemies!")
        tribute1.add_enemy(tribute2)
        tribute2.add_enemy(tribute1)
        return [tribute1, tribute2]


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

    def execute(self) -> list[Tribute]:

        mutt = random.choice(self.mutts_list)
        print(f"{mutt.capitalize()} have been released!")

        for tribute in self.tributes:
            d6 = random.randint(1, 6)

            if d6 in [1]:
                # killed outright
                print(f"{tribute.name} was killed by the {mutt}!")
                tribute.kill()
            if d6 in [2, 3]:
                # severe injury
                print(f"{tribute.name} was severely wounded by the {mutt}!")
                tribute.adjust_health(-5)
            if d6 in [4, 5]:
                # wounded!
                print(f"{tribute.name} was slightly wounded by the {mutt}!")
                tribute.adjust_health(-3)
            if d6 in [6]:
                # escaped!
                print(f"{tribute.name} escaped the {mutt}!")
                tribute.adjust_health(-1)

        if all(tribute.is_dead for tribute in self.tributes):
            print("All tributes were killed womp womp")

        return self.tributes


class EventFood(EventBase):
    num_participants = 1

    def execute(self) -> list[Tribute]:
        tribute = random.sample(self.tributes, k=self.num_participants)[0]
        print(f"{tribute.name} found some food!")
        tribute.hunger += 2
        return [tribute]


class EventDrink(EventBase):
    num_participants = 1

    def execute(self) -> list[Tribute]:
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

        return [tribute]


class EventGetEquipment(EventBase):
    num_participants = 1

    def execute(self) -> list[Tribute]:
        tribute = random.sample(self.tributes, k=self.num_participants)[0]
        valid_equipment = [
            equipment for equipment, quantity in self.gamemaker.equipment.items() if quantity > 0
        ]
        if len(valid_equipment) == 0:
            print("No equipment left to find, womp womp!")
            return [tribute]
        equipment = random.choice(valid_equipment)
        new_equipment = deepcopy(equipment)

        tribute.update_conditions()

        # Evaluate whether the tribute would become encumbered after picking up the item
        projected_equipment = tribute.equipment + [new_equipment]
        projected_encumbrance = sum(getattr(item, "weight", 0) for item in projected_equipment)
        projected_is_encumbered = (
            projected_encumbrance > 5
            if "Backpack" not in [item.name for item in projected_equipment]
            else projected_encumbrance > 10
        )
        should_use_encumbered_logic = tribute.is_encumbered() or projected_is_encumbered

        if not should_use_encumbered_logic:
            # remove one of the equipment from the gamemaker's inventory
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
        else:
            if random.random() < 0.5:
                print(f"{tribute.name} found {new_equipment.name} but is carrying too much to pick it up!")
            elif 0.5 <= random.random() < 0.8:
                random_equipment = random.choice(tribute.equipment)
                print(f"{tribute.name} found {new_equipment.name}. They dropped {random_equipment.name} to pick it up instead.")
                tribute.equipment.remove(random_equipment)
                tribute.equipment.append(new_equipment)
            else:
                print(f"{tribute.name} found {new_equipment.name}. They have too much stuff already, but managed to pick it up anyway!")
                tribute.equipment.append(new_equipment)

        tribute.update_conditions()
        return [tribute]


class EventUseEquipment(EventBase):
    num_participants = 1

    def execute(self) -> list[Tribute]:
        tributes_with_equipment = [
            tribute for tribute in self.tributes if len(tribute.equipment) > 0
        ]
        if len(tributes_with_equipment) == 0:
            return []

        tribute = random.choice(tributes_with_equipment)

        for equipment in tribute.equipment:
            if equipment.fighting_bonus > 0:
                continue

            if equipment.name == "First Aid Kit" and 'Healer' in tribute.trait:
                print(f"{tribute.name} is a Healer and used {equipment.name} more effectively!")
                keep_charge = random.random() < 0.6
                if keep_charge:
                    print(f"{tribute.name} was so efficient the kept the {equipment.name} for another use!")
                    equipment.charges += 1
                else:
                    print(f"{tribute.name} used up the {equipment.name}.")
            else:
                print(f"{tribute.name} is using {equipment}.")

            # Apply equipment effects
            tribute.hunger += equipment.hunger_bonus
            tribute.thirst += equipment.thirst_bonus
            tribute.adjust_health(equipment.health_bonus)

            # Remove equipment if it has limited charges
            equipment.use()
            if equipment.is_broken:
                print(f"{equipment.name} is gone!")
                tribute.equipment.remove(equipment)
                tribute.encumbrance -= equipment.weight
            else:
                print(f"{equipment.name} has {equipment.charges} uses left.")

        return [tribute]


class EventSponsorGift(EventBase):
    num_participants = 1
    possible_gifts = [
        Equipment(name="Medicine", health_bonus=8, charges=1),
        Equipment(name="Wine", thirst_bonus=5, charges=3),
        Equipment(name="Bread", hunger_bonus=4, charges=4),
        Equipment(name="Spile", thirst_bonus=1, charges=-1, comfort_bonus=-1),
        Equipment(name="Water Purifier", charges=3),
        Equipment(name="Fire starter kit", charges=3, comfort_bonus=3),
        Equipment(name="Backpack", weight=1, charges=-1),
    ]

    def execute(self) -> list[Tribute]:
        weights = [3 if "Popular" in tribute.trait else 1 for tribute in self.tributes]
        tribute = random.choices(self.tributes, weights=weights, k=1)[0]
        gift = random.choice(self.possible_gifts)
        gift = deepcopy(gift)
        print(f"{tribute.name} received a sponsor gift: {gift}!")
        tribute.equipment.append(gift)
        tribute.encumbrance += gift.weight
        return [tribute]


class EventExposure(EventBase):
    num_participants = 1

    def execute(self) -> list[Tribute]:
        tribute = random.sample(self.tributes, k=self.num_participants)[0]

        if random.random() < 0.5:
            print(f"{tribute.name} is exposed to intense heat!")
            tribute.comfort += 1
            if tribute.comfort > 0:
                protected = False
                for equipment in tribute.equipment:
                    if equipment.comfort_bonus < 0:
                        print(f"{tribute.name} is protected from the heat by {equipment.name}!")
                        tribute.comfort += equipment.comfort_bonus
                        protected = True
                        return [tribute]
                if not protected:
                    tribute.adjust_health(-1)
        else:
            print(f"{tribute.name} is exposed to bitter cold!")
            tribute.comfort -= 1
            if tribute.comfort < 0:
                protected = False
                for equipment in tribute.equipment:
                    if equipment.comfort_bonus > 0:
                        print(f"{tribute.name} is protected from the cold by {equipment.name}!")
                        tribute.comfort += equipment.comfort_bonus
                        protected = True
                        return [tribute]
                if not protected:
                    tribute.adjust_health(-1)

        return [tribute]


class EventBloodbath(EventBase):
    num_participants = -1  # All tributes participate

    def execute(self) -> list[Tribute]:
        print("The Bloodbath has begun at the Cornucopia!")
        for tribute in self.tributes:
            # Randomly assign a starting position in the arena
            tribute.coords = [random.randint(0, 0), random.randint(0, 0)]  # all tributes start at cornucopia

        # Track initial number of tributes so we can end the event early
        initial_count = len(self.tributes)

        # Randomly determine if each tribute is killed in the bloodbath
        for tribute in self.tributes:
            if "Career" in tribute.trait:
                if random.random() < 0.1:  # 10% chance of being killed
                    print(f"{tribute.name} was killed in the bloodbath!")
                    tribute.kill()
                else:
                    print(f"{tribute.name} survived the bloodbath!")
            else:
                if random.random() < 0.3:  # 30% chance of being killed
                    print(f"{tribute.name} was killed in the bloodbath!")
                    tribute.kill()
                else:
                    print(f"{tribute.name} survived the bloodbath!")

            # If living tributes drop to half (or less) of initial, end the bloodbath early
            alive_count = sum(1 for t in self.tributes if not t.is_dead)
            if alive_count <= initial_count / 2:
                break

            # Allow tributes to pick up equipment if they survive the bloodbath
            if not tribute.is_dead:
                # Randomly determine if they find equipment
                if random.random() < 0.5:  # 50% chance of finding equipment
                    bloodbath_equipment = list(self.gamemaker.equipment.keys()) + list(
                        EventSponsorGift.possible_gifts
                    )
                    valid_equipment = [
                        equipment for equipment in bloodbath_equipment if equipment in self.gamemaker.equipment or equipment in EventSponsorGift.possible_gifts
                    ]
                    if len(valid_equipment) > 0:
                        equipment = random.choice(valid_equipment)
                        new_equipment = deepcopy(equipment)
                        print(f"{tribute.name} found {new_equipment.name} at the cornucopia!")
                        tribute.equipment.append(new_equipment)
                        tribute.update_conditions()
                        if equipment in self.gamemaker.equipment:
                            self.gamemaker.equipment[equipment] -= 1

        return self.tributes

class EventForage(EventBase):
    num_participants = 1

    possible_items = {
        "food": Equipment(name="food", hunger_bonus=2, charges=1),
        "meat": Equipment(name="meat", hunger_bonus=3, charges=1),
        "poison berries": Equipment(name="poison berries", health_bonus=-3, charges=1),
        "medicinal herbs": Equipment(name="medicinal herbs", health_bonus=3, charges=1),
    }

    def execute(self) -> list[Tribute]:
        tribute = random.sample(self.tributes, k=self.num_participants)[0]
        print(f"{tribute.name} is foraging for resources!")

        found_items = ["food", "nothing"]
        weights = [0.5, 0.5]

        if "Healer" in tribute.trait:
            found_items.append("medicinal herbs")
            weights = [0.3, 0.1, 0.6]
        elif "Hunter" in tribute.trait:
            found_items.append("meat")
            weights = [0.4, 0.05, 0.55]
        elif "Intelligent" in tribute.trait:
            found_items.append("poison berries")
            weights = [0.6, 0.35, 0.05]
        else:
            found_items.append("poison berries")
            weights = [0.6, 0.35, 0.1]

        chosen_item = random.choices(found_items, weights=weights, k=1)[0]
        print(f"{tribute.name} found {chosen_item} while foraging!")

        # Apply effects based on what they found
        if chosen_item == "food":
            tribute.hunger += 2
            print(f"{tribute.name} ate the food and gained 2 hunger points!")
        elif chosen_item == "medicinal herbs":
            if "First aid kit" in tribute.equipment:
                print(f"{tribute.name} added the medicinal herbs to their First Aid Kit and gained an extra use!")
                tribute.equipment["First aid kit"].charges += 1
            else:
                tribute.adjust_health(+3)
                print(f"{tribute.name} used the medicinal herbs and gained 3 health points!")
        elif chosen_item == "meat":
            tribute.hunger += self.possible_items["meat"].hunger_bonus
            print(f"{tribute.name} ate the meat and gained {self.possible_items['meat'].hunger_bonus} hunger points!")
        elif chosen_item == "poison berries":
            tribute.adjust_health(self.possible_items["poison berries"].health_bonus)
            print(f"{tribute.name} ate the poison berries and lost {-self.possible_items['poison berries'].health_bonus} health points!")
        else:
            print(f"{tribute.name} found nothing while foraging!")

        return [tribute]
