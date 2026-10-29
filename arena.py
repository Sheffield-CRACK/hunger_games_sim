import numpy as np

from tribute import Tribute

class Arena:
    """A class representing the game arena."""

    def __init__(self, size: int):
        self.size = size

        # Create a 2D grid to represent the arena
        self.grid = np.zeros((size, size), dtype=object)

        # Create locations for each cell in the grid
        for i, j in np.ndindex(self.grid.shape):
            self.grid[i, j] = Location(arena=self, coords=[i, j])

    def __repr__(self) -> str:
        return f"Arena(size={self.size}x{self.size})"

    @property
    def locations(self) -> list["Location"]:
        """Return a list of all locations in the arena."""
        return [self.grid[i, j] for i, j in np.ndindex(self.grid.shape)]

    def get_location(self, coords: list[int]) -> "Location":
        """Get the location at the given coordinates."""
        x, y = coords
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[x, y]
        else:
            raise ValueError(f"Coordinates {coords} are out of bounds for arena size {self.size}.")

    def get_neighbouring_locations(self, coords: list[int], distance=1) -> list["Location"]:
        """Get the neighbouring locations of the given coordinates."""
        x, y = coords
        neighbours = []
        for dx in np.arange(-distance, distance + 1):
            for dy in np.arange(-distance, distance + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    neighbours.append(self.grid[nx, ny])
        return neighbours

    def show_map(self):
        """Display the arena map with number of tributes in each location."""
        for i in range(self.size):
            row = []
            for j in range(self.size):
                location = self.grid[i, j]
                if location.tributes:
                    row.append(f" {len(location.tributes):<2}")  # Show number of tributes
                else:
                    row.append(" . ")
            print(" ".join(row))


class Location:
    """A location in the arena."""

    def __init__(self, arena: Arena, coords: list[int]):
        self.arena = arena
        self.coords = coords
        self.tributes: list[Tribute] = []

    def __repr__(self) -> str:
        return f"Location({self.coords})"

    def get_neighbours(self, distance: int = 1):
        """Neighbouring locations of this location within the specified distance."""
        return self.arena.get_neighbouring_locations(self.coords, distance)

    def add_tribute(self, tribute: Tribute):
        """Add a tribute to this location."""
        # first remove the tribute from its current location if it has one
        current_location = tribute.location
        if current_location is not None:
            print(current_location.tributes)
            current_location.tributes.remove(tribute)

        # now add the tribute to this location
        self.tributes.append(tribute)
        tribute.location = self
