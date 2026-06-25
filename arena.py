from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from perlin_noise import generate_fractal_noise_2d
from typing import Literal, Any

ArenaBiome = Literal["plains", "forest", "desert", "mountain"]

HeightMode = Literal["flattened", "normal", "amplified"]
TreeMode = Literal["dense", "normal", "oasis"]

TERRAIN_TYPES = [
    "forest",
    "grass",
    "sand",
    "rock",
    "snow",
    "water",
]

BIOMES: dict[ArenaBiome, Any] = {
    "plains": {
        "ground": "grass",
        "height": "default",
        "trees": "default",
    },
    "forest": {
        "ground": "grass",
        "height": "default",
        "trees": "dense",
    },  # default
    "desert": {
        "ground": "sand",
        "height": "flattened",
        "trees": "oasis",
    },  # flatten height map
    "mountain": {"ground": "grass", "height": "amplified", "trees": "hill_forest"},
}

# class PerlinNoise:
#     def __init__(self, size: int, seed: int | None = None) -> None:
#         self.size = size

#         self.rng = np.random.default_rng(seed)
#         self.gradient_vectors = np.zeros((size, size, 2))
#         for i in range(0,size):
#             for j in range(0,size):
#                 vector = self.rng.random(2)
#                 vector = vector / np.sqrt(np.sum(vector**2))
#                 self.gradient_vectors[i,j,:] = vector


class Arena:
    def __init__(self, biome: ArenaBiome, seed: int = 0, world_size: int = 32) -> None:
        self.biome = biome
        self.seed = seed
        self.world_size = world_size

        self.ground_type = BIOMES[biome]["ground"]
        self.height_type = BIOMES[biome]["height"]
        self.tree_type = BIOMES[biome]["trees"]

        self.rng = np.random.default_rng(seed)
        self.grid_points = np.arange(0, world_size)
        self.noise_grid_points = np.arange(0, world_size + 1)

        self.terrain_type = [
            ["grass" for _ in range(0, world_size)] for _ in range(0, world_size)
        ]
        self.terrain_height = np.zeros((world_size, world_size))
        self.equipment_count = np.zeros((world_size, world_size))
        self.start_location = [0, 0]

        self.generate_terrain()
        self.generate_structures()

    def generate_terrain(self) -> None:
        height_noise = generate_fractal_noise_2d(
            (self.world_size, self.world_size),
            (self.world_size / 16, self.world_size / 16),
            octaves=5,
            seed=self.seed,
        )
        height_noise += 1
        height_noise = height_noise / 2
        self.terrain_height = height_noise
        print(np.min(height_noise), np.max(height_noise))
        print("Noise:", height_noise)

        vegetation_noise = generate_fractal_noise_2d(
            (self.world_size, self.world_size),
            (self.world_size / 16, self.world_size / 16),
            octaves=2,
            seed=self.seed + 1,
        )
        vegetation_noise += 1
        vegetation_noise = vegetation_noise / 2
        print(np.min(vegetation_noise), np.max(vegetation_noise))
        print("Noise:", vegetation_noise)

        plt.imshow(vegetation_noise)
        plt.show()

        for i in range(0, self.world_size):
            for j in range(0, self.world_size):
                height = height_noise[i, j]
                vegetation = vegetation_noise[i, j]
                if height < 0.2:
                    self.terrain_type[i][j] = "water"

                elif height < 0.3 and height >= 0.2:
                    if vegetation > 0.6:
                        self.terrain_type[i][j] = "forest"
                    elif vegetation < 0.4:
                        self.terrain_type[i][j] = "rock"
                    else:
                        self.terrain_type[i][j] = "sand"

                elif height < 0.7 and height >= 0.3:
                    if vegetation > 0.7:
                        self.terrain_type[i][j] = "forest"
                    else:
                        self.terrain_type[i][j] = self.ground_type

                elif height >= 0.7:
                    self.terrain_type[i][j] = "snow"

    def generate_trees(self) -> None:
        vegetation_noise = generate_fractal_noise_2d(
            (self.world_size, self.world_size),
            (self.world_size / 16, self.world_size / 16),
            octaves=2,
            seed=self.seed + 1,
        )
        vegetation_noise += 1
        vegetation_noise = vegetation_noise / 2
        print(np.min(vegetation_noise), np.max(vegetation_noise))
        print("Noise:", vegetation_noise)

        plt.imshow(vegetation_noise)
        plt.show()

        for i in range(0, self.world_size):
            for j in range(0, self.world_size):
                height = self.terrain_height[i, j]
                vegetation = vegetation_noise[i, j]

                match self.tree_type:
                    case "dense":
                        if height < 0.7 and height >= 0.3:
                            if vegetation > 0.7:
                                self.terrain_type[i][j] = "forest"

                    case "normal":
                        if height < 0.7 and height >= 0.3:
                            if vegetation > 0.7:
                                self.terrain_type[i][j] = "forest"
                        elif height < 0.3 and height >= 0.2:
                            if vegetation > 0.6:
                                self.terrain_type[i][j] = "forest"

                    case "oasis":
                        if height < 0.4 and height >= 0.3:
                            if vegetation > 0.7:
                                self.terrain_type[i][j] = "forest"
                    case _:
                        raise ValueError("Invalid tree mode")

    def generate_structures(self) -> None:
        # Set the start point
        candidate_points = []

        for i in range(8, self.world_size - 8):
            for j in range(8, self.world_size - 8):
                # if len(candidate_points) >= 64:
                #     break

                terrain = self.terrain_type[i][j]
                if terrain == "grass":
                    candidate_points += [[i, j]]

        self.start_location = self.rng.choice(candidate_points, 1)[0].tolist()

    def print_map(self, player_counts: np.ndarray) -> None:
        for i in range(0, self.world_size):
            row = ""
            for j in range(0, self.world_size):
                if player_counts[i, j] > 0:
                    row += f"{int(player_counts[i, j]):02d}"
                    continue

                if list(self.start_location) == [i, j]:
                    row += "X "
                    continue

                match self.terrain_type[i][j]:
                    case "grass":
                        row += "# "
                    case "forest":
                        row += "^ "
                    case "rock":
                        row += "o "
                    case "sand":
                        row += ". "
                    case "snow":
                        row += "* "
                    case "water":
                        row += "~ "
                    case _:
                        row += "? "

            print(row)


# if __name__ == "__main__":
#     arena = Arena("forest", 0, 32)
#     arena.print_map()
