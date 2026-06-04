from __future__ import annotations

import json

from events import *
from gamemaker import GameMaker
from tribute import Tribute

if __name__ == "__main__":
    with open("tributes.json", encoding="utf-8") as f_in:
        tributes_data = json.load(f_in)

    if not isinstance(tributes_data, list):
        raise ValueError("tributes.json must contain a list of objects")

    tributes: list[Tribute] = []
    for d in tributes_data:
        tributes += [
            Tribute(
                name=d["name"],
                district=d["district"],
                rank=d["rank"],
                trait=d.get("trait"),  # if not given, set to None
            )
        ]

    game = GameMaker(tributes)
    game.run_game()
