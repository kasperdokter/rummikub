from dataclasses import dataclass, field

from rummikub.tile import Tile, Location


@dataclass
class GameState:
    tiles: list[Tile] = field(default_factory=list)

    def __str__(self):
        table = ' '.join(str(t) for t in self.tiles if t.location == Location.TABLE)
        board = ' '.join(str(t) for t in self.tiles if t.location == Location.BOARD)
        return f"Tafel: {table}\nBordje: {board}"