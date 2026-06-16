from __future__ import annotations

import json

from gamemaker import GameMaker
from tribute import Tribute

if __name__ == "__main__":
    with open("tributes.json", encoding="utf-8") as f_in:
        tributes_data = json.load(f_in)

    if not isinstance(tributes_data, list):
        raise ValueError("tributes.json must contain a list of objects")

    tributes: list[Tribute] = []
    for d in tributes_data:
        tribute = Tribute(
            name=d["name"],
            district=d["district"],
            rank=d["rank"],
            trait=d.get("trait"),  # if not given, set to None
        )
        setattr(tribute, "_temp_allies", d.get("allies", []))  # store allies temporarily
        tributes.append(tribute)

    # Set up alliances (need to do this after all tributes are created)
    for tribute in tributes:
        tribute.allies = [t for t in tributes if t.name in getattr(tribute, "_temp_allies", [])]
        delattr(tribute, "_temp_allies")  # remove temporary attribute

    game = GameMaker(tributes)
    game.run_game()
